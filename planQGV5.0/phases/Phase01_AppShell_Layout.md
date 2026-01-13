# Phase 01 — App Shell layout (sidebar + main) + single-scroll structure

## Purpose
Introduce the two-column shell and required DOM anchors without changing data behavior.

## Contracts referenced
- `contracts/APP_SHELL_DOM_CONTRACT.md`
- `immutables/IMMUTABLES.md` (I1, I5, I6, I7)

## Files to modify
- `views/web/index.html`
- `views/web/styles.css`

## Step-by-step tasks

### 1) Update index.html to include shell containers
Add the following structural containers (exact IDs per contract):
- `#app-shell`
  - `#app-sidebar`
    - `#section-nav` (empty at first; filled in Phase 02)
  - `#app-main`
    - existing toolbar/header stays here
    - `#scroll-container` remains inside main as the single scroll root
Add `#toast-container` near end of body.

Important: do NOT change existing IDs used by JS (keep them intact).

### 2) Update CSS to support a two-column layout
- Use CSS grid or flex:
  - Sidebar fixed width (e.g., 260–320px)
  - Main area fills remaining width
- Ensure `#scroll-container` is the only scroll region.
- Make toolbar sticky (optional in this phase; required by Phase 06 outcome).

### 3) Add minimal styles for sidebar list items
- `.section-nav-item` base style
- `.section-nav-item.active` highlight style

## Tests that must pass
1. App launches with the new layout.
2. Categories render as before.
3. Switching quote type still works.
4. No JS errors due to missing IDs.

## Success checklist
- [ ] Shell layout exists with required IDs.
- [ ] Single scroll root remains correct (`#scroll-container`).
- [ ] No behavior regressions.
