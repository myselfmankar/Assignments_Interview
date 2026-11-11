# Job board starter

A small job board for an insiderOne work sample. It is made up: the jobs and
companies are not real.

## Run it

You need Node 20 or newer. There are no packages to install.

```
npm start      # then open http://localhost:3000
npm test       # runs the tests in test/
```

## What is here

- `server.js`: the web server. `GET /api/jobs?q=` lists jobs, `GET /api/saved` gets saved jobs, `POST /api/saved` saves a job, `DELETE /api/saved/:jobId` removes a saved job, and `GET /` serves the page.
- `lib/jobs.js`: reading and searching the jobs. Pure functions.
- `lib/saved.js`: saved jobs business logic (pure helper functions, atomic file persistence, and lock serialization).
- `jobs.json`: the jobs catalog.
- `saved-jobs.json`: persisted list of saved job IDs.
- `public/`: the page (`index.html`) and client script (`app.js`).
- `test/`: tests using Node's built-in test runner (`jobs.test.js`, `saved.test.js`).

## Saved Jobs Feature

### What was built
1. **Save button on jobs**: Each job item in the list includes an interactive Save button that calls `POST /api/saved`. Once saved, the button transitions to a disabled "Saved" state.
2. **Saved jobs list**: A "Saved jobs" section on the same page displays all saved jobs with full details (title, company, location, stipend).
3. **Remove saved jobs**: Each saved job includes a "Remove" button that issues `DELETE /api/saved/:jobId`, removes it from the saved list, and re-enables the Save button in the main listing.
4. **Backend API**:
   - `POST /api/saved`: Expects `{ "jobId": "..." }`. Validates input, returns `201 Created` with job details. Deduplicates repeat saves and returns `404 Not Found` with a clear message for unknown job IDs (no server crashes).
   - `GET /api/saved`: Returns an array of full job objects for all currently saved jobs.
   - `DELETE /api/saved/:jobId`: Removes the job ID from storage and returns `200 OK`, or `404 Not Found` if the job is not in the saved list.
5. **Persistence**: Saved job IDs are stored on disk in `saved-jobs.json`. When the page or server reloads, all saved jobs remain preserved.
6. **Automated tests**: Unit tests for pure helper functions and file storage, plus end-to-end HTTP integration tests for all API routes, edge cases, error responses, and restart persistence using Node's native test runner (`node:test` and `node:assert/strict`).

### How to run it and the tests
```bash
# Start the web server
npm start
# Open http://localhost:3000 in your browser

# Run the test suite
npm test
```

### One decision made and why
- **Decision**: Storing normalized job IDs (`["j1", "j2"]`) in `saved-jobs.json` rather than copying complete job objects, paired with an async promise lock (`withSaveLock`) for disk operations.
- **Why**: Maintaining `jobs.json` as the single source of truth prevents data duplication and ensures that any updates to a job (e.g. stipend revisions, title or location updates) are automatically and accurately reflected in the saved jobs list. Concurrency locking prevents file corruption when concurrent requests read and write to `saved-jobs.json`.

