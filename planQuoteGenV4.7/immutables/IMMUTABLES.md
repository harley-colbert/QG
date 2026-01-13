# Immutables (Must NOT change)

These are non-negotiable constraints for this refactor. Any deviation is a plan failure.

## I1 — Keep headers.py identical
- File: `models/headers.py`
- Requirement: **Byte-for-byte identical** to the source snapshot.
- Allowed: None (no formatting, no import sorting, no whitespace edits).

## I2 — Keep the app architecture
- Remains a PyWebView desktop app.
- Entry point remains `main.py`.
- `views/web/index.html` remains the UI entry.

## I3 — Preserve XML root + tag naming rules
- XML root element remains `<QuoteData>`.
- Quote type is stored under `<quoteType>` (when present).
- Data elements are emitted as sanitized tags from their full keys.
- Tag sanitizer behavior remains:
  - keep dots in tag names
  - replace non `[A-Za-z0-9_.-]` with `_`
  - prefix tags starting with digits with `n`

## I4 — Preserve the “field key” namespace convention
- Frontend/back-end field keys remain `data.<Category>.<FieldName>` (and dynamic variants).
- Dynamic categories still use numeric suffix keys (e.g., `.0`, `.1`, ...).

## I5 — Preserve existing user flows
- Users can: New Quote → Fill → Save XML → Open XML → Submit → Generate Word.
- Optional categories and dynamic sections continue to work.

## I6 — No new formatted text / HTML storage
- After this change, **no field** is allowed to store HTML as its canonical value.
- Any legacy HTML encountered must be converted to plain text at load or save time.

## I7 — Remove Quill completely
- No Quill JS/CSS assets.
- No Quill imports in JS.
- No backend Quill/Delta/HTML conversion pipeline in Word export.
- Repo audit must show zero hits for:
  - `quill`
  - `ql-`
  - `dangerouslyPasteHTML`

## I8 — Keep logging style (but rename Quill-specific prefixes)
- Logging remains verbose and useful.
- Any log prefix referencing Quill (e.g., `[QUILL2DOC]`) must be renamed to neutral `[WORD]` or similar.
