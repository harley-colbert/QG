# Agent 03 — Collapsible sections with persisted state

## Objective
Add collapse/expand behavior per category and persist it in localStorage.

## Files to modify
- `views/web/js/main.js`
- `views/web/styles.css`

## Tasks
1. Update category group DOM:
   - Add `.category-header` wrapper for the title
   - Add a toggle button/icon
   - Attach click handler to toggle `.collapsed` on `.category-group`
2. Persist:
   - localStorage key `qg.collapse.<type>.<categorySlug>`
3. Apply persisted state:
   - during render, read storage and apply `.collapsed`
4. CSS:
   - `.category-group.collapsed .fields-container { display:none; }`

## Tests
1. Collapse a section; fields hide
2. Expand; fields return with values intact
3. Restart app; collapse state persists
4. Budgetary and Final have separate persistence

## Evidence
- Screenshot of collapsed sections + persisted after restart

## Exit criteria
- Collapse works and does not lose data.
