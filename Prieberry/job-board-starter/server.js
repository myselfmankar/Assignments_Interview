// A small job board: a JSON API and one page. Run with `npm start`.
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { loadJobs, searchJobs, findJob } from "./lib/jobs.js";
import {
  loadSaved,
  saveSaved,
  addSavedJob,
  removeSavedJob,
  getSavedJobs,
  withSaveLock,
} from "./lib/saved.js";

const PORT = Number(process.env.PORT ?? 3000);

function sendJson(res, status, body) {
  res.writeHead(status, { "content-type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(body));
}

async function readJson(req) {
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(chunk);
  }
  const text = Buffer.concat(chunks).toString("utf8");
  if (!text.trim()) return {};
  return JSON.parse(text);
}

export function createApp(options = {}) {
  const jobsPath = options.jobsPath ?? new URL("./jobs.json", import.meta.url);
  const savedPath = options.savedPath ?? new URL("./saved-jobs.json", import.meta.url);

  return createServer(async (req, res) => {
    try {
      const url = new URL(req.url ?? "/", "http://localhost");

      // GET /api/jobs?q=...
      if (req.method === "GET" && url.pathname === "/api/jobs") {
        const jobs = await loadJobs(jobsPath);
        return sendJson(res, 200, searchJobs(jobs, url.searchParams.get("q")));
      }

      // GET /api/saved
      if (req.method === "GET" && url.pathname === "/api/saved") {
        const [jobs, savedIds] = await Promise.all([
          loadJobs(jobsPath),
          loadSaved(savedPath),
        ]);
        const savedJobs = getSavedJobs(jobs, savedIds);
        return sendJson(res, 200, savedJobs);
      }

      // POST /api/saved
      if (req.method === "POST" && url.pathname === "/api/saved") {
        let body;
        try {
          body = await readJson(req);
        } catch {
          return sendJson(res, 400, { error: "Invalid JSON body" });
        }

        const jobId = typeof body?.jobId === "string" ? body.jobId.trim() : "";
        if (!jobId) {
          return sendJson(res, 400, { error: "jobId is required" });
        }

        const jobs = await loadJobs(jobsPath);
        const job = findJob(jobs, jobId);
        if (!job) {
          return sendJson(res, 404, { error: `Job not found: ${jobId}` });
        }

        await withSaveLock(async () => {
          const savedIds = await loadSaved(savedPath);
          const nextSavedIds = addSavedJob(savedIds, jobId);
          await saveSaved(nextSavedIds, savedPath);
        });

        return sendJson(res, 201, { success: true, ...job, job });
      }

      // DELETE /api/saved/:jobId
      if (req.method === "DELETE" && url.pathname.startsWith("/api/saved/")) {
        const rawId = url.pathname.slice("/api/saved/".length);
        const jobId = decodeURIComponent(rawId).trim();
        if (!jobId) {
          return sendJson(res, 400, { error: "jobId is required" });
        }

        let found = false;
        await withSaveLock(async () => {
          const savedIds = await loadSaved(savedPath);
          if (savedIds.includes(jobId)) {
            found = true;
            const nextSavedIds = removeSavedJob(savedIds, jobId);
            await saveSaved(nextSavedIds, savedPath);
          }
        });

        if (!found) {
          return sendJson(res, 404, { error: `Job not found in saved list: ${jobId}` });
        }

        return sendJson(res, 200, { success: true, jobId });
      }

      if (req.method === "DELETE" && url.pathname === "/api/saved") {
        return sendJson(res, 400, { error: "jobId is required" });
      }

      // Static files
      if (req.method === "GET" && (url.pathname === "/" || url.pathname === "/app.js")) {
        const file = url.pathname === "/" ? "index.html" : "app.js";
        const type = file.endsWith(".html") ? "text/html" : "text/javascript";
        const body = await readFile(new URL(`./public/${file}`, import.meta.url));
        res.writeHead(200, { "content-type": `${type}; charset=utf-8` });
        return res.end(body);
      }

      sendJson(res, 404, { error: "Not found" });
    } catch (err) {
      console.error(err);
      sendJson(res, 500, { error: "Something went wrong" });
    }
  });
}

// Started directly (npm start), not imported by a test.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  createApp().listen(PORT, () => console.log(`Job board on http://localhost:${PORT}`));
}
