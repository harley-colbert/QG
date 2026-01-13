# Agent 02 — Section navigation (sidebar list + click-to-jump + active highlight)

## Objective
Create and wire section navigation module.

## Files to add
- `views/web/js/sectionNav.js`

## Files to modify
- `views/web/js/main.js`
- `views/web/js/dynamicSections.js` (only if needed)

## Tasks
1. Implement `sectionNav.js`:
   - scan `.category-group` under `#scroll-container`
   - ensure each has `id` and `data-category`
   - build `.section-nav-item` list inside `#section-nav`
   - click-to-scroll within `#scroll-container`
   - IntersectionObserver root must be `#scroll-container`
2. Wire into `main.js`:
   - after renderCategories: call `rebuildSectionNav()`
   - on quote type change: call `rebuildSectionNav()`
3. If dynamic content changes categories:
   - call `rebuildSectionNav()` after dynamic add/remove

## Tests
1. Sidebar lists all sections
2. Clicking a nav item scrolls correctly
3. Scrolling updates active highlight
4. Switching quote type updates nav list

## Evidence
- short screen recording or notes verifying click-to-jump + active highlight

## Exit criteria
- Section nav works and is stable across rerenders.
