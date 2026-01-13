# Phase 02 — Section navigation (build list + click-to-jump + active highlight)

## Purpose
Implement the sidebar section index and active section highlighting.

## Contracts referenced
- `contracts/SECTION_NAV_CONTRACT.md`
- `contracts/APP_SHELL_DOM_CONTRACT.md`
- `immutables/IMMUTABLES.md` (I7)

## Files to add
- `views/web/js/sectionNav.js`

## Files to modify
- `views/web/js/main.js`
- `views/web/js/dynamicSections.js` (only if dynamic changes require nav rebuild)

## Step-by-step tasks

### 1) Create sectionNav.js
Export:
- `initSectionNav({ scrollRootId, navRootId })`
- `rebuildSectionNav()`

Implementation requirements:
- Find all `.category-group` under `#scroll-container`
- Ensure each has:
  - stable `id` (assign one if missing, using a slug from `data-category`)
  - `data-category` (if missing, derive from header text and set it)
- Build `.section-nav-item` entries inside `#section-nav`
- Click handler scrolls `#scroll-container` to the target element:
  - use `element.scrollIntoView({ behavior: "smooth", block: "start" })`
  - OR compute scrollTop within the scroll root
- IntersectionObserver:
  - root = `#scroll-container`
  - threshold: ~0.25–0.5
  - add/remove `.active` on matching nav item

### 2) Wire into main.js
After categories render:
- call `initSectionNav()` once
- call `rebuildSectionNav()` after each render / quote type switch

### 3) Handle dynamic sections if necessary
If adding/removing dynamic content changes `.category-group` list:
- call `rebuildSectionNav()` after dynamic updates

## Tests that must pass
1. Sidebar lists all sections after render.
2. Clicking a section scrolls to the correct category.
3. Manual scroll updates active highlight.
4. Switching quote type rebuilds the nav correctly.

## Success checklist
- [ ] Section nav works and is stable across rerenders.
- [ ] Active highlight works using #scroll-container as observer root.
