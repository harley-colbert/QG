# Agent 00 — Preflight UX audit + baseline

## Objective
Confirm the current DOM and rendering flow so later phases can wrap the UI safely.

## Tasks
1. Launch QuoteGenV4.7 and confirm:
   - Budgetary renders
   - Final renders
2. Inspect (DevTools):
   - identify the scroll container element (target: `#scroll-container`)
   - confirm `.category-group` wrappers exist for each section
   - confirm there is a clear header/title node per category
3. Locate primary JS render:
   - `views/web/js/main.js` renderCategories / createCategoryGroup
4. Locate dynamic section handlers:
   - `views/web/js/dynamicSections.js`

## Tests
- Manual: open app, switch quote type, scroll, open modals

## Evidence to capture
- List of the existing IDs and class names used by current JS to find and populate content
- Confirmed scroll root element and whether there are nested scrollbars

## Exit criteria
- You can point to the exact elements and functions we will hook in Phase 01/02.
