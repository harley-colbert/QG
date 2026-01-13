# JS API Contract (PyWebViewAPI ↔ Frontend)

Source file (reference): `views/pywebview_api.py`

This refactor MUST preserve the public JS-callable API shapes (method names and return types), unless explicitly noted below.

## Methods in-scope for this refactor

### open_quote() -> dict
Returns an object:
- `quoteType`: string, `"budgetary"` or `"final"`
- `quotes`: dict
  - used for UI header/quote lists
- `fields`: dict
  - a map of fieldKey -> string value
  - fieldKey typically begins with `data.`

### save_quote(quote_type: string) -> None
- Persists the current quote data as XML via the ViewModel.
- Assumes JS previously pushed updated values via `set_all_fields(...)`.

### submit_quote(quote_type: string) -> dict or None
- Generates the Word output using the configured template pipeline.
- After this refactor: Word submission must be plain-text only (no HTML conversion).

### get_all_fields() -> dict
- Returns current field map as used by the frontend store.
- After this refactor, this should return **flat field keys** (see VIEWSTORE_CONTRACT).

### set_all_fields(flat_map: dict) -> None
- Accepts flat fieldKey->value and merges into Quote data.

### set_field(full_key: str, value: str) -> None
- Sets a single field value.

## Allowed behavior changes (explicitly allowed)
- If legacy stored values contain HTML, the backend may return cleaned plain text in `fields`.
- If submitted values contain HTML, the backend must sanitize to plain text before persistence/export.

## Prohibited changes
- Renaming methods
- Changing `open_quote()` return keys
- Returning nested dicts in `fields` (must be flat map)
