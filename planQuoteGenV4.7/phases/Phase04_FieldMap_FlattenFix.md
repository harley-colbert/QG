# Phase 04 — Fix field map consistency (Flatten contract)

## Purpose
Ensure backend `open_quote()` returns `fields` as a **flat** fieldKey→string map aligned with the frontend viewStore contract.

Why this matters:
- `viewStore` is flat.
- `open_quote()` promises a flat map for repopulating inputs.
- Any nested dict returned here breaks repopulation and causes subtle bugs.

## Contracts referenced
- `contracts/VIEWSTORE_CONTRACT.md`
- `contracts/JS_API_CONTRACT.md`
- `immutables/IMMUTABLES.md` (I4)

## Files to modify (exact paths)
- `viewmodels/quote_viewmodel.py`
- Possibly `models/quote_model.py` (only if flatten/unflatten helpers live there)

## Step-by-step tasks
1. Implement/restore a robust flatten helper:
   - Input: nested dict rooted at `quote.data`
   - Output: flat dict with keys prefixed by `data.`
2. Update `QuoteViewModel.get_all_fields()`:
   - Must return the flat dict (never the nested dict).
3. Ensure `set_all_fields()` remains the inverse:
   - Accept flat keys, merge into nested structure
   - Preserve dynamic keys and numeric suffix behavior.

## Tests that must pass
1. New quote:
   - Save XML
   - Open XML
   - Confirm all fields repopulate
2. Dynamic sections:
   - Add multiple dynamic entries
   - Save/Open
   - Confirm all entries repopulate and keep their numeric suffix ordering
3. Confirm `open_quote()` returns:
   - `fields` where every key is a string containing at least one dot and begins with `data.`

## Success checklist
- [ ] `get_all_fields()` returns a flat dict.
- [ ] No UI repopulation regressions.
- [ ] Dynamic fields repopulate reliably.
