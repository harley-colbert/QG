# Phase 00 — Preflight + Safety Nets

## Purpose
Establish a clean baseline, identify all Quill touchpoints, and create repeatable audit checks.

## Scope
No functional changes to app behavior in this phase. Only inspection + audit tooling.

## Files touched
- (Optional) Add audit scripts under `tools/`
- No production code modifications required in Phase 00.

## Step-by-step tasks
1. Unzip and run the app once to confirm baseline startup.
2. Inventory Quill touchpoints by searching the repo for:
   - `quill`
   - `ql-`
   - `dangerouslyPasteHTML`
3. Record all matches and map each to one of:
   - Frontend asset
   - Frontend runtime reference
   - Backend Word conversion
4. Create two audit scripts (one Windows PowerShell, one bash) that fail if any prohibited token is found.

## Tests that must pass
- App launches and UI loads without error (baseline).
- Audit scripts correctly report Quill findings in the unmodified repo.

## Success checklist
- [ ] You have a definitive list of Quill touchpoints (with file paths).
- [ ] You have a repeatable “no-quill” audit command/script ready for later phases.
