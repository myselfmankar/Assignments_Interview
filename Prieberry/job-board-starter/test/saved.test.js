import { test, describe, before, after } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

import {
  addSavedJob,
  removeSavedJob,
  getSavedJobs,
  loadSaved,
  saveSaved,
} from "../lib/saved.js";
import { loadJobs } from "../lib/jobs.js";
import { createApp } from "../server.js";

describe("saved jobs pure functions", async () => {
  const jobs = await loadJobs();

  test("addSavedJob adds job id when not already present", () => {
    const list = ["j1"];
    const updated = addSavedJob(list, "j2");
    assert.deepEqual(updated, ["j1", "j2"]);
    // Original list is not mutated
    assert.deepEqual(list, ["j1"]);
  });

  test("addSavedJob keeps exactly one copy when adding the same job twice", () => {
    const list = ["j1", "j2"];
    const updated = addSavedJob(list, "j1");
    assert.deepEqual(updated, ["j1", "j2"]);
    assert.equal(updated.filter((id) => id === "j1").length, 1);
  });

  test("addSavedJob ignores empty or non-string id", () => {
    assert.deepEqual(addSavedJob(["j1"], ""), ["j1"]);
    assert.deepEqual(addSavedJob(["j1"], null), ["j1"]);
  });

  test("removeSavedJob removes an existing job id", () => {
    const list = ["j1", "j2", "j3"];
    const updated = removeSavedJob(list, "j2");
    assert.deepEqual(updated, ["j1", "j3"]);
    // Original list is not mutated
    assert.deepEqual(list, ["j1", "j2", "j3"]);
  });

  test("removeSavedJob returns same items when id is not in the list", () => {
    const list = ["j1", "j2"];
    const updated = removeSavedJob(list, "j99");
    assert.deepEqual(updated, ["j1", "j2"]);
  });

  test("getSavedJobs returns full job objects and omits missing ids", () => {
    const savedJobs = getSavedJobs(jobs, ["j1", "j99", "j2"]);
    assert.equal(savedJobs.length, 2);
    assert.equal(savedJobs[0].id, "j1");
    assert.equal(savedJobs[0].title, "Data Analyst Intern");
    assert.equal(savedJobs[1].id, "j2");
    assert.equal(savedJobs[1].company, "Kite Learning");
  });
});

describe("saved jobs file persistence", () => {
  let tempDir;
  let tempFileUrl;

  before(async () => {
    tempDir = await mkdtemp(join(tmpdir(), "job-board-test-"));
    tempFileUrl = pathToFileURL(join(tempDir, "saved-test.json"));
  });

  after(async () => {
    if (tempDir) {
      await rm(tempDir, { recursive: true, force: true });
    }
  });

  test("loadSaved returns empty array when file does not exist", async () => {
    const missingUrl = pathToFileURL(join(tempDir, "nonexistent.json"));
    const result = await loadSaved(missingUrl);
    assert.deepEqual(result, []);
  });

  test("saveSaved and loadSaved persist and restore saved IDs", async () => {
    await saveSaved(["j1", "j4", "j1"], tempFileUrl);
    const result = await loadSaved(tempFileUrl);
    // saveSaved deduplicates ids
    assert.deepEqual(result, ["j1", "j4"]);
  });
});

describe("saved jobs HTTP API", () => {
  let server;
  let baseUrl;
  let tempDir;
  let tempFileUrl;

  before(async () => {
    tempDir = await mkdtemp(join(tmpdir(), "job-board-api-test-"));
    tempFileUrl = pathToFileURL(join(tempDir, "saved-api.json"));

    const app = createApp({ savedPath: tempFileUrl });
    await new Promise((resolve) => {
      server = app.listen(0, resolve);
    });
    const { port } = server.address();
    baseUrl = `http://localhost:${port}`;
  });

  after(async () => {
    if (server) {
      await new Promise((resolve) => server.close(resolve));
    }
    if (tempDir) {
      await rm(tempDir, { recursive: true, force: true });
    }
  });

  test("GET /api/saved returns empty list initially", async () => {
    const res = await fetch(`${baseUrl}/api/saved`);
    assert.equal(res.status, 200);
    const body = await res.json();
    assert.deepEqual(body, []);
  });

  test("POST /api/saved saves a job and returns 201", async () => {
    const res = await fetch(`${baseUrl}/api/saved`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ jobId: "j1" }),
    });
    assert.equal(res.status, 201);
    const body = await res.json();
    assert.equal(body.id, "j1");
    assert.equal(body.title, "Data Analyst Intern");

    // Verify GET /api/saved reflects the saved job
    const listRes = await fetch(`${baseUrl}/api/saved`);
    const list = await listRes.json();
    assert.equal(list.length, 1);
    assert.equal(list[0].id, "j1");
  });

  test("POST /api/saved saving the same job twice keeps one copy", async () => {
    const res = await fetch(`${baseUrl}/api/saved`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ jobId: "j1" }),
    });
    assert.ok(res.status === 200 || res.status === 201);

    const listRes = await fetch(`${baseUrl}/api/saved`);
    const list = await listRes.json();
    assert.equal(list.length, 1);
    assert.equal(list[0].id, "j1");
  });

  test("POST /api/saved returns 404 clear error for unknown job ID without crashing", async () => {
    const res = await fetch(`${baseUrl}/api/saved`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ jobId: "unknown-job-id" }),
    });
    assert.equal(res.status, 404);
    const body = await res.json();
    assert.ok(body.error && body.error.includes("Job not found"));

    // Server is still alive and operational
    const pingRes = await fetch(`${baseUrl}/api/jobs`);
    assert.equal(pingRes.status, 200);
  });

  test("POST /api/saved returns 400 for missing or invalid jobId", async () => {
    const res1 = await fetch(`${baseUrl}/api/saved`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({}),
    });
    assert.equal(res1.status, 400);

    const res2 = await fetch(`${baseUrl}/api/saved`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: "invalid json string",
    });
    assert.equal(res2.status, 400);
  });

  test("DELETE /api/saved/:jobId removes saved job", async () => {
    // Add a second job first
    await fetch(`${baseUrl}/api/saved`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ jobId: "j2" }),
    });

    const resDelete = await fetch(`${baseUrl}/api/saved/j1`, {
      method: "DELETE",
    });
    assert.equal(resDelete.status, 200);

    // Verify j1 is removed, j2 remains
    const listRes = await fetch(`${baseUrl}/api/saved`);
    const list = await listRes.json();
    assert.equal(list.length, 1);
    assert.equal(list[0].id, "j2");
  });

  test("DELETE /api/saved/:jobId returns 404 for job not in saved list", async () => {
    const res = await fetch(`${baseUrl}/api/saved/nonexistent`, {
      method: "DELETE",
    });
    assert.equal(res.status, 404);
    const body = await res.json();
    assert.ok(body.error && body.error.includes("not found"));
  });

  test("Saved jobs persist across application restart", async () => {
    // Spin up a second server instance pointing to the same temp file
    const newApp = createApp({ savedPath: tempFileUrl });
    let newServer;
    await new Promise((resolve) => {
      newServer = newApp.listen(0, resolve);
    });
    const newPort = newServer.address().port;

    try {
      const res = await fetch(`http://localhost:${newPort}/api/saved`);
      assert.equal(res.status, 200);
      const list = await res.json();
      assert.equal(list.length, 1);
      assert.equal(list[0].id, "j2");
    } finally {
      await new Promise((resolve) => newServer.close(resolve));
    }
  });
});
