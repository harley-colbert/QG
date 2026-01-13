# Phase 03 — Collapsible sections with persisted state

## Purpose
Allow users to collapse/expand categories and persist their preference.

## Contracts referenced
- `contracts/COLLAPSE_STATE_CONTRACT.md`
- `contracts/APP_SHELL_DOM_CONTRACT.md`

## Files to modify
- `views/web/js/main.js`
- `views/web/styles.css`

## Step-by-step tasks

### 1) Update category group rendering to include a clickable header
In `createCategoryGroup(...)` (or wherever the category DOM is built):
- Wrap the title area in a `.category-header`
- Add a toggle button/icon (chevron)
- Add click handler:
  - toggles `.collapsed` on `.category-group`
  - writes localStorage key `qg.collapse.<type>.<slug>`

### 2) Apply saved collapse state during render
When category groups are created:
- compute slug from `data-category`
- read localStorage key for current quote type
- if true: apply `.collapsed`

### 3) CSS collapse behavior
- `.category-group.collapsed .fields-container { display: none; }`
- Ensure padding/margins still look clean.

### 4) Optional: add “Collapse all / Expand all”
This can be a small control block in sidebar or toolbar.
If added:
- it updates localStorage for all categories and re-renders or toggles in-place.

## Tests that must pass
1. Collapse a section; its fields hide.
2. Values are preserved (no re-registration bugs, no lost input).
3. Restart app; same sections remain collapsed.
4. Switching quote type uses separate collapse state storage.

## Success checklist
- [ ] Collapse works reliably.
- [ ] State persists.
- [ ] No value loss.
