# Agent 05 — Form readability + optional completion badges

## Objective
Improve form layout (labels/spacing) and optionally show completion badges in sidebar.

## Files to add (optional)
- `views/web/js/validation.js`

## Files to modify
- `views/web/styles.css`
- `views/web/js/sectionNav.js` (if adding badges)
- `views/web/js/main.js` (if needed)

## Tasks
1. CSS form readability (required):
   - implement label-above-input or responsive grid
   - ensure no field keys/names change
2. Optional compact density:
   - toggle class and reduce spacing
3. Optional completion badges:
   - compute missingCount per category
   - show badge or check in sidebar
   - debounce updates on input change

## Tests
- Labels no longer wrap awkwardly
- No layout breakage in common window sizes
- Optional: badges update correctly

## Evidence
- Before/after screenshot of a section with previously-wrapping labels

## Exit criteria
- Form is noticeably easier to scan.
