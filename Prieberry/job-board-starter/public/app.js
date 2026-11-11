const jobsList = document.getElementById("jobs");
const savedList = document.getElementById("saved-jobs");
const search = document.getElementById("search");

let currentJobs = [];
let savedJobIds = new Set();

async function fetchSavedJobs() {
  const res = await fetch("/api/saved");
  if (!res.ok) throw new Error("Failed to load saved jobs");
  return res.json();
}

async function renderSaved() {
  const savedJobs = await fetchSavedJobs();
  savedJobIds = new Set(savedJobs.map((j) => j.id));
  savedList.innerHTML = "";

  if (savedJobs.length === 0) {
    const emptyLi = document.createElement("li");
    emptyLi.className = "empty-msg";
    emptyLi.textContent = "No saved jobs yet.";
    savedList.append(emptyLi);
    return;
  }

  for (const job of savedJobs) {
    const li = document.createElement("li");

    const info = document.createElement("span");
    info.className = "job-info";
    info.textContent = `${job.title} at ${job.company}, ${job.location}. Rs ${job.stipend.toLocaleString("en-IN")} a month.`;

    const removeBtn = document.createElement("button");
    removeBtn.className = "remove-btn";
    removeBtn.textContent = "Remove";
    removeBtn.setAttribute("aria-label", `Remove ${job.title} from saved jobs`);

    removeBtn.addEventListener("click", async () => {
      removeBtn.disabled = true;
      try {
        const res = await fetch(`/api/saved/${encodeURIComponent(job.id)}`, {
          method: "DELETE",
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          alert(err.error || "Failed to remove job");
          removeBtn.disabled = false;
          return;
        }
        await refresh();
      } catch (err) {
        console.error(err);
        removeBtn.disabled = false;
      }
    });

    li.append(info, removeBtn);
    savedList.append(li);
  }
}

function renderJobs(jobs) {
  jobsList.innerHTML = "";
  for (const job of jobs) {
    const li = document.createElement("li");

    const info = document.createElement("span");
    info.className = "job-info";
    info.textContent = `${job.title} at ${job.company}, ${job.location}. Rs ${job.stipend.toLocaleString("en-IN")} a month.`;

    const saveBtn = document.createElement("button");
    const isSaved = savedJobIds.has(job.id);
    saveBtn.className = isSaved ? "saved-btn" : "save-btn";
    saveBtn.textContent = isSaved ? "Saved" : "Save";
    saveBtn.disabled = isSaved;
    saveBtn.setAttribute("aria-label", `Save ${job.title}`);

    saveBtn.addEventListener("click", async () => {
      saveBtn.disabled = true;
      try {
        const res = await fetch("/api/saved", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ jobId: job.id }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          alert(err.error || "Failed to save job");
          saveBtn.disabled = false;
          return;
        }
        await refresh();
      } catch (err) {
        console.error(err);
        saveBtn.disabled = false;
      }
    });

    li.append(info, saveBtn);
    jobsList.append(li);
  }
}

async function refresh() {
  await renderSaved();
  renderJobs(currentJobs);
}

async function show(query = "") {
  const res = await fetch(`/api/jobs?q=${encodeURIComponent(query)}`);
  currentJobs = await res.json();
  await refresh();
}

search.addEventListener("input", () => show(search.value));
show();
