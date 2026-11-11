import { readFile, writeFile } from "node:fs/promises";
import { findJob } from "./jobs.js";

export const DEFAULT_SAVED_PATH = new URL("../saved-jobs.json", import.meta.url);

let saveLockQueue = Promise.resolve();

/**
 * Serializes file operations so concurrent requests do not corrupt saved-jobs.json.
 */
export function withSaveLock(fn) {
  const result = saveLockQueue.then(fn);
  saveLockQueue = result.catch(() => {});
  return result;
}

/**
 * Loads the array of saved job IDs from disk.
 * Returns an empty array if the file does not exist or is empty.
 */
export async function loadSaved(path = DEFAULT_SAVED_PATH) {
  try {
    const raw = await readFile(path, "utf8");
    if (!raw.trim()) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    if (err.code === "ENOENT") {
      return [];
    }
    throw err;
  }
}

/**
 * Persists the array of saved job IDs to disk as JSON.
 */
export async function saveSaved(ids, path = DEFAULT_SAVED_PATH) {
  const uniqueIds = Array.from(new Set(ids));
  await writeFile(path, JSON.stringify(uniqueIds, null, 2), "utf8");
}

/**
 * Pure function: adds a job ID to the saved list, keeping exactly one copy.
 */
export function addSavedJob(savedIds, jobId) {
  if (!jobId || typeof jobId !== "string") return [...savedIds];
  if (savedIds.includes(jobId)) {
    return [...savedIds];
  }
  return [...savedIds, jobId];
}

/**
 * Pure function: removes a job ID from the saved list.
 */
export function removeSavedJob(savedIds, jobId) {
  return savedIds.filter((id) => id !== jobId);
}

/**
 * Pure function: maps saved IDs to full job objects from the jobs catalogue.
 * Omits any IDs that cannot be found.
 */
export function getSavedJobs(jobs, savedIds) {
  return savedIds.map((id) => findJob(jobs, id)).filter(Boolean);
}
