# Agent 04 — Status + Dirty tracking + Toast feedback + Submit safety

## Objective
Show file/dirty/last-saved; provide toasts; improve Submit UX.

## Files to add
- `views/web/js/toast.js`

## Files to modify
- `views/web/index.html`
- `views/web/js/viewStore.js`
- `views/web/js/main.js`
- `views/web/js/submissionModal.js`
- `views/pywebview_api.py` (recommended)

## Tasks
1. Add status elements to toolbar:
   - `#status-file`, `#status-dirty`, `#status-last-saved`
2. Implement toast module:
   - success/error/info
3. Add uiMeta helpers in viewStore.js:
   - setActiveFile, setLastSaved, markDirty, clearDirty, getUiMeta
4. Wire dirty tracking:
   - any input change marks dirty
5. Wire actions:
   - Save/Open/New/Submit show toasts + update status
6. Submit safety:
   - disable Submit during execution
   - show spinner/progress
7. Backend additions (recommended):
   - open_quote returns path
   - save_quote returns {path, savedAt}
   - frontend handles legacy None too

## Tests
1. Edit field -> dirty on
2. Save -> dirty off, last saved updated, toast shows
3. Open -> file shown, dirty off, toast shows
4. Submit -> button disables, toast shows on finish

## Evidence
- Screenshot showing status updated + toast displayed

## Exit criteria
- Status and toasts are reliable; Submit is safer.
