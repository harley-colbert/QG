# Status + Dirty Tracking Contract

Goal: show (a) current file, (b) dirty state, (c) last saved.

## Frontend store fields (recommendation)
In `views/web/js/viewStore.js`, add a small UI meta store:

- `uiMeta[type] = { activePath, dirty, lastSavedAt }`

## Required public helpers (frontend)
- `setActiveFile(type, pathString)`
- `setLastSaved(type, isoString)`
- `markDirty(type)`
- `clearDirty(type)`
- `getUiMeta(type)`

## Dirty rules
- Any user edit to an input/textarea/select marks dirty for that quote type.
- Saving clears dirty and updates lastSavedAt.
- Opening a quote clears dirty and sets activePath.
- New quote clears activePath (or sets to “Unsaved”) and clears dirty initially.

## Display
- `#status-file` shows basename of path (not full path) if possible.
- `#status-dirty` shows visible indicator only when dirty is true.
- `#status-last-saved` shows “Last saved: …” if known, else blank.

## Prohibited
- Dirty tracking must not interfere with field value tracking.
- Dirty tracking must not block typing with expensive DOM scans.
