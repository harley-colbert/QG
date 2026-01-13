# Agent 04 — Field map consistency: Flatten `fields` map

## Primary objective
Ensure backend returns a flat `fields` map aligned with frontend viewStore expectations.

## Inputs
- Plan phase: `phases/Phase04_FieldMap_FlattenFix.md`
- Contracts:
  - `contracts/VIEWSTORE_CONTRACT.md`
  - `contracts/JS_API_CONTRACT.md`

## Files to modify
- `viewmodels/quote_viewmodel.py` (primary)
- Optional helper location if needed:
  - `models/quote_model.py`

## Implementation guidance (strict)
1. `get_all_fields()` must return:
   - a flat dict: `data.<...>.<...>` -> string
2. Preserve dynamic keys:
   - numeric suffixes are part of the key
3. Ensure set_all_fields remains inverse behavior:
   - merges flat keys into nested data structure

## Tests to run (must)
1. New quote with dynamic entries:
   - add multiple dynamic items
   - save/open
   - confirm repopulation exact
2. Confirm open_quote() returns:
   - `fields` keys all begin with `data.` and are strings

## Evidence to capture
- Sample `fields` output snippet showing flat keys
- Confirmation that UI repopulates without special cases

## Exit criteria
- Backend/frontend are aligned on a flat fields contract.
