# JS API Compatibility Contract

Primary interface: `views/pywebview_api.py`

## Must preserve
- Existing method names
- Existing return keys from `open_quote()`:
  - `quoteType`
  - `quotes`
  - `fields`

## Allowed additions (recommended)
To support improved status UI:

### open_quote() additions
- `path` (string): path to opened XML file (or basename)

### save_quote() return
Change from `None` to:
- `{ "path": "<saved_path>", "savedAt": "<iso8601>" }`

This is backward-compatible if frontend accepts either:
- `None` (older behavior)
- dict with metadata (new behavior)

## Prohibited
- Removing keys from open_quote payload
- Returning nested dicts in `fields` (must remain flat)
