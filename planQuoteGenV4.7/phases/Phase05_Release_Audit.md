# Phase 05 — Repo audit, smoke tests, and release packaging

## Purpose
Confirm full Quill removal, validate core flows end-to-end, and produce the final release artifact.

## Contracts referenced
- All contracts
- `immutables/IMMUTABLES.md`

## Step-by-step tasks

### 1) Run the “no-quill” audit
- Verify zero matches for:
  - `quill`
  - `ql-`
  - `dangerouslyPasteHTML`

### 2) Full smoke test flow
1. New quote (budgetary)
   - Fill multiple categories including formerly-rich description fields (multi-line)
   - Save XML
2. Open the saved XML
   - Confirm all values repopulate as plain text
3. Submit quote
   - Confirm Word output is generated
   - Confirm the document contains readable plain text
4. Repeat for final quote type (if applicable).

### 3) Packaging
- Ensure deleted files are not present.
- Ensure `models/headers.py` remains byte-for-byte identical (re-verify hash).
- Zip the completed repo as:
  - `QuoteGenV4.7.zip` (release artifact name expectation)

## Tests that must pass
- Audit: zero prohibited token hits
- Smoke tests: budgetary + final flows pass
- Word output is generated and contains no HTML artifacts

## Success checklist
- [ ] Repo contains zero Quill dependencies or references.
- [ ] All description inputs are plain textareas.
- [ ] Save/Open/Submit work end-to-end.
- [ ] Release zip created with expected name.
