# Phase 06 — Release audit + packaging

## Purpose
Validate end-to-end behavior and produce the release zip.

## Files touched
- None required (verification + packaging only).

## Step-by-step tasks
1. Run the full smoke test plan in `tests/TEST_PLAN.md`.
2. Confirm no regressions in:
   - dynamic sections
   - contacts/settings/submission modals
3. Verify keyboard navigation and focus states remain visible.
4. Package as:
   - `QuoteGenV5.0.zip`

## Tests that must pass
- All items in `tests/TEST_PLAN.md`
- All items in `tests/DEFINITION_OF_DONE.md`

## Success checklist
- [ ] Definition of Done satisfied.
- [ ] Release zip created with correct name.
