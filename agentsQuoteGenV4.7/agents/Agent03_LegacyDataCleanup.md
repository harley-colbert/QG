# Agent 03 — Legacy Data Cleanup (Old XML with HTML)

## Primary objective
Ensure older XML files saved with Quill/HTML load into the UI as plain text and are re-saved as plain text.

## Inputs
- Plan phase: `phases/Phase03_LegacyData_Cleanup.md`
- Contract:
  - `contracts/TEXT_SANITIZATION_CONTRACT.md`

## Files likely involved (choose the cleanest place; document the choice)
- `models/quote_model.py`
- `viewmodels/quote_viewmodel.py`

## Implementation guidance (strict)
1. Use the same sanitizer logic across:
   - load
   - set_field / set_all_fields
   - save
2. Preserve paragraph intent:
   - convert `<br>` and paragraph boundaries to `\n` prior to stripping tags

## Tests to run (must)
1. Open a legacy XML containing HTML tags:
   - UI should display plain text, not tags
2. Save it again:
   - Spot-check resulting XML for the absence of `<p>`, `<br>`, etc.

## Evidence to capture
- Before/after snippet of a legacy value (raw vs cleaned)
- Note where normalization was implemented (model vs viewmodel)

## Exit criteria
- Legacy files open cleanly and re-save without HTML.
