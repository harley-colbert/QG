# Agent 01 — Frontend: Remove Quill UI and replace with `<textarea>`

## Primary objective
Delete Quill assets and remove all Quill runtime code, replacing rich editors with plain `<textarea>` while keeping field keys unchanged.

## Inputs
- Plan phase: `phases/Phase01_Frontend_RemoveQuill.md`
- Contracts:
  - `contracts/VIEWSTORE_CONTRACT.md`
  - `contracts/JS_API_CONTRACT.md`
- Immutables:
  - Do NOT modify `models/headers.py`.

## Files to delete (verify they exist; delete if present)
- `views/web/quill.bundle.mjs`
- `views/web/quill.js`
- `views/web/quill.snow.css`
- `views/web/js/quill.bundle.mjs`
- `views/web/js/quill.esm.js`
- `views/web/js/quillSetup.js`

## Files to modify
- `views/web/index.html`
- `views/web/js/dynamicSections.js`
- `views/web/js/main.js`
- `views/web/js/viewStore.js`
- `views/web/styles.css`

## Implementation guidance (strict)
1. Preserve field keys:
   - Any control for a field must keep `name="<fieldKey>"` and/or `data-field-key="<fieldKey>"`.
2. Treat textarea like other controls:
   - `.value` is the source of truth
   - viewStore stores strings only
3. Remove Quill lifecycle concepts:
   - no register/unregister quill instances
   - no rehydrate step
4. Remove Quill styling blocks:
   - remove `.ql-*` style rules

## Tests to run (must)
1. Launch UI:
   - no console errors
   - no missing module import errors
2. New quote:
   - fill multiline text in description fields
   - save
3. Open saved quote:
   - verify multiline text repopulates
4. Dynamic sections:
   - add 2+ entries
   - save/open
   - verify repopulation

## Evidence to capture
- Screenshot or paste of console showing no errors
- Notes of which files were deleted
- One example field key showing correct textarea binding

## Exit criteria
- UI has no Quill code and all rich fields are textareas.
- Save/open works and preserves multiline content.
