# Phase 01 — Frontend: Remove Quill UI and convert to `<textarea>`

## Purpose
Remove Quill from the UI entirely and replace all rich text editors with plain textareas while preserving field keys and persistence.

## Contracts referenced
- `contracts/VIEWSTORE_CONTRACT.md`
- `contracts/JS_API_CONTRACT.md`
- `immutables/IMMUTABLES.md` (I4, I5, I7)

## Files to delete (exact paths)
- `views/web/quill.bundle.mjs`
- `views/web/quill.js`
- `views/web/quill.snow.css`
- `views/web/js/quill.bundle.mjs`
- `views/web/js/quill.esm.js`
- `views/web/js/quillSetup.js`

## Files to modify (exact paths)
- `views/web/index.html`
- `views/web/js/dynamicSections.js`
- `views/web/js/main.js`
- `views/web/js/viewStore.js`
- `views/web/styles.css`

## Step-by-step tasks

### 1) Remove Quill from index.html
- Remove the Quill CSS link (`quill.snow.css`).
- Remove importmap entry that aliases `"quill"` to a local bundle.
- Remove any scripts that import Quill directly.

### 2) Replace Quill editor creation in dynamicSections.js
- Remove: `import { initQuill } from './quillSetup.js';`
- For any field previously rendered as a Quill container `<div>`, render:
  - `<textarea>`
  - Must keep the exact same field key bindings:
    - `name="<fieldKey>"`
    - and/or `data-field-key="<fieldKey>"` (whichever is used elsewhere)
- Ensure the textarea is registered with the viewStore system exactly as other controls.

### 3) Remove Quill rehydration logic in main.js
- Remove imports and calls related to:
  - `rehydrateQuills`
  - `initQuill`
- Ensure `innerApply()` applies values to textareas just like other controls.
- Ensure “New quote” flow does not call Quill rehydrate.

### 4) Remove Quill plumbing from viewStore.js
- Remove any quillInstances tracking.
- Remove any Quill-specific branches in:
  - `applyViewStore(type)`
  - `saveViewStore(type)`
- After change: treat textarea like any other input and store `.value` as string.

### 5) Remove Quill styling from styles.css
- Delete the “Rich-text (Quill) Editor Styles” section.
- Add minimal textarea styling if needed:
  - width: 100%
  - reasonable min-height
  - readable font size
  - resizable

## Tests that must pass
1. **UI loads with zero console errors** (especially module import errors).
2. Create a new quote:
   - Enter multi-line text into formerly-rich description fields.
   - Save XML.
3. Open that XML:
   - All textarea fields repopulate correctly.
   - Dynamic sections still repopulate correctly.
4. Run the audit scripts:
   - Quill files are gone, so audit should show fewer hits (but may still find backend refs until Phase 02).

## Success checklist
- [ ] No Quill assets remain in `views/web/`.
- [ ] No JS imports reference Quill.
- [ ] All formerly rich text fields are plain `<textarea>`.
- [ ] Save/Open preserves textarea content and line breaks.
