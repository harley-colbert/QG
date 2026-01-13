# Phase 04 — Status + Dirty tracking + Toast feedback

## Purpose
Make system state visible and provide non-modal feedback for actions.

## Contracts referenced
- `contracts/STATUS_DIRTY_CONTRACT.md`
- `contracts/TOAST_CONTRACT.md`
- `contracts/JS_API_COMPAT_CONTRACT.md`

## Files to add
- `views/web/js/toast.js`

## Files to modify
- `views/web/index.html`
- `views/web/js/viewStore.js`
- `views/web/js/main.js`
- `views/web/js/submissionModal.js`
- `views/pywebview_api.py` (recommended for richer metadata)

## Step-by-step tasks

### 1) Add status elements to toolbar area (index.html)
Add elements (IDs per contract):
- `#status-file`, `#status-dirty`, `#status-last-saved`

### 2) Implement toast.js
- Create toast container logic under `#toast-container`
- Export `toastSuccess/toastError/toastInfo`

### 3) Update viewStore.js for uiMeta tracking
Add:
- `uiMeta = { budgetary: {...}, final: {...} }`
- helper functions:
  - setActiveFile, setLastSaved, markDirty, clearDirty, getUiMeta
Wire `markDirty` to input change listeners (main.js).

### 4) Wire toasts + status updates in main.js
- On Save success: toastSuccess + clearDirty + setLastSaved + setActiveFile
- On Open success: toastSuccess + clearDirty + setActiveFile
- On New: toastInfo + clearDirty + activePath resets
- On failure: toastError with message
- Ensure dirty flips on any value change.

### 5) Submit UX improvements
In submission flow (main.js or submissionModal.js):
- Disable Submit while running.
- Show spinner/progress text.
- Toast on completion/failure.

### 6) Backend metadata (recommended)
In `views/pywebview_api.py`:
- `open_quote()` returns `path`
- `save_quote()` returns `{ path, savedAt }`
Frontend should handle both legacy `None` and new dict payload.

## Tests that must pass
1. Edit a field → dirty indicator appears.
2. Save → dirty clears, last saved updates, toast appears.
3. Open → file name updates, dirty clears, toast appears.
4. Submit → submit disables during run; success/fail toast appears.
5. No regressions in modals.

## Success checklist
- [ ] Status area reflects reality.
- [ ] Toast feedback works for all major actions.
- [ ] Submit UX is safer and clearer.
