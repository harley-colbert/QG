# Definition of Done (Global)

The refactor is considered complete ONLY when all items below are true.

## D1 — Quill is fully removed
- No Quill assets (JS/CSS) exist in the repo
- No JS imports reference Quill
- No runtime code assumes Quill exists
- No backend modules convert Quill Delta or HTML to Word

## D2 — Plain text everywhere
- UI uses `<textarea>` for all formerly formatted/rich inputs
- ViewStore stores plain strings only
- Backend stores plain text only (no HTML, no Delta JSON)
- Legacy HTML is cleaned on load and on save

## D3 — Word export is plain text only
- Word generation inserts plain text for every field
- Multiline text is preserved in a readable way
- No HTML tags appear in output docs

## D4 — Contracts & immutables satisfied
- `models/headers.py` unchanged byte-for-byte
- Field key naming remains `data.*`
- XML root/tag sanitizer behavior unchanged
- Backend API shape preserved per contracts

## D5 — Smoke tests pass
- New quote → fill → save → open → submit works
- Budgetary and final flows pass (if both are used)
- Dynamic sections still function across save/open

## D6 — Release artifact produced
- Zip named: `QuoteGenV4.7.zip`
