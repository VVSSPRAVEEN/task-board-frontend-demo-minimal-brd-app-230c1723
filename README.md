# Task Board

Single-file task board delivered for FR13 (responsive accessible UX) and FR14 (delivery documentation). No build step, no backend.

## Files

- `index.html` - self-contained app: semantic HTML5, inline CSS3 (3-column desktop, stacked at 360px and below, visible `:focus-visible` rings) and inline ES2020 JavaScript.
- `README.md` - this document.

## Preview

From the project root:

```
python -m http.server 8000
```

Open http://localhost:8000/index.html in the latest Chromium-based desktop browser. Stop the server with Ctrl+C.

## Prerequisites

- Python 3.8 or newer (only for the static preview server).
- A modern Chromium-based browser (current Chrome or Edge) with JavaScript enabled and `localStorage` available.

## Environment variables

None. The application reads no environment variables and requires no secrets; all state lives in the browser's `localStorage`.

| Variable | Purpose | Required / Default | Secret |
| --- | --- | --- | --- |
| (none) | - | - | - |

## Architecture

- Single entrypoint `index.html` containing inline CSS and inline ES2020 JavaScript; no build step, bundler or backend.
- Domain services run in-page: task lifecycle manager, validation guard, filter engine, persistence adapter, confirmation coordinator, seed/reset manager.
- The persistence adapter uses `localStorage` key `taskboard.v1` holding `{ tasks: Task[], initializedFlag: boolean }`, where `Task` is exactly `{ id, title, description, status }`.
- User-supplied values are rendered with `textContent`; data is never injected as HTML.

## Run, test, build, deploy

- Run (local preview): `python -m http.server 8000`, then open http://localhost:8000/index.html.
- Test: run the four manual acceptance checks in the table below and record step, observed and pass/fail.
- Build: none; the deliverable is the source files as-is.
- Deploy: copy `index.html` and `README.md` to any static file host and serve them over HTTP(S).

## Troubleshooting

- Board appears empty: check `localStorage.getItem('taskboard.v1')`; if the key is absent the samples reseed on reload, and if `initializedFlag` is true with `tasks: []` the empty board is intentional.
- Warning that saved data could not be read: the stored value is not valid JSON and is left untouched. Clear it in DevTools > Application > Local Storage to persist new edits.
- Changes do not survive refresh: the browser is blocking `localStorage` (private mode or site data restrictions); the board keeps working in memory only.
- Port 8000 already in use: run `python -m http.server 8080` and use http://localhost:8080/index.html.

## Behaviour summary

- Statuses and order: To do, In progress, Done. Each task carries a labeled status selector for moving it between columns.
- Validation: title is required and limited to 80 characters after trimming; description is limited to 280 characters.
- Search is case-insensitive over title and description and combines (AND) with the status filter.
- Persistence: `localStorage` key `taskboard.v1` stores `{ tasks, initializedFlag }`.
- A missing key seeds exactly: "Plan the demo" in To do, "Build the task board" in In progress, "Review requirements" in Done.
- A present empty array stays empty across refresh because `initializedFlag` is true.
- Corrupt or unreadable storage shows a visible warning and continues in memory without overwriting the stored value until an explicit edit or reset.
- Delete and Reset demo data both require confirmation; Cancel preserves the current state. Reset also clears the search and status filter.

## Manual acceptance checks

Recorded in the latest Chromium-based desktop browser against http://localhost:8000/index.html.

| # | Check | Step | Observed | Pass/Fail |
| --- | --- | --- | --- | --- |
| 1 | First-use samples seed once | Clear `taskboard.v1` for the origin (DevTools > Application > Local Storage), then reload the page twice. | Three cards appear: "Plan the demo" in To do, "Build the task board" in In progress, "Review requirements" in Done. `taskboard.v1` holds three tasks with `initializedFlag: true`, and the second reload does not duplicate them. | Pass |
| 2 | Intentionally empty board stays empty | Delete all three tasks (confirm each), then reload the page. | The board is still empty and `taskboard.v1` holds `{"tasks":[],"initializedFlag":true}`; no sample tasks reappear. | Pass |
| 3 | Corrupt storage warns and is not overwritten | Run `localStorage.setItem('taskboard.v1','{not json')` in the console, then reload the page. | A visible warning states the saved board data could not be read, the board still works in memory, and `localStorage.getItem('taskboard.v1')` still returns `{not json` after reload without an edit. | Pass |
| 4 | Delete and Reset honour Cancel vs confirm | Add a task, type a search term, pick a status filter, then click Delete and Cancel; click Reset demo data and Cancel. Then delete with OK and reset with OK. | Cancel leaves the task, the search text and the status filter unchanged. OK deletes the task, and Reset restores the three sample tasks while clearing the search box and status filter. | Pass |
