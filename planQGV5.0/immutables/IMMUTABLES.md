# Immutables (Must NOT change)

These constraints are non-negotiable. Any violation is a plan failure.

## I1 — Preserve QuoteGen core architecture
- Remains a PyWebView desktop app.
- Entry point remains `main.py`.
- UI entry remains `views/web/index.html`.

## I2 — Preserve data contracts and field keys
- Field key namespace remains `data.*`.
- Dynamic keys keep numeric suffix rules.
- Existing XML compatibility must remain (open older quotes).

## I3 — Preserve backend public API names
- PyWebView API method names remain stable (no renames).
- Adding additional return metadata is allowed, but removing/renaming existing keys is not.

## I4 — Preserve headers.py
- File: `models/headers.py`
- Must remain byte-for-byte identical.

## I5 — No framework rewrite
- Keep vanilla HTML/CSS/JS modules in `views/web/`.
- No React/Vue/Svelte migration.
- No build step required for the UI (keep current workflow).

## I6 — Preserve existing admin modals and flows
- Contacts and Settings modals continue to function.
- Submission modal continues to function.

## I7 — Maintain “single source of truth” for values
- `views/web/js/viewStore.js` remains the canonical store of field values.
- UI enhancements must not create competing state stores for field values.

## I8 — Accessibility must not regress
- Keyboard navigation must continue to work.
- Visible focus outlines must not be removed.
- Contrast on primary text must remain readable.
