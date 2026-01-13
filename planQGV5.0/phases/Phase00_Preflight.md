# Phase 00 — Preflight UX audit + baseline

## Purpose
Confirm the current UI’s DOM structure and rendering flow so we can safely wrap it with a shell and add navigation/collapse without breaking behavior.

## Files touched
- None required (inspection only).
- Optional: add a small `tools/` note file if desired.

## Step-by-step tasks
1. Unzip `QuoteGenV4.7.zip` and run the app.
2. Identify the primary scroll root:
   - confirm `#scroll-container` exists and is the scrollable element.
3. Confirm category blocks render with:
   - `.category-group`
   - a title/header element
   - a container that holds the fields (used later for collapse)
4. Confirm JS render entry points:
   - `views/web/js/main.js` renders categories
   - `dynamicSections.js` adds/removes dynamic rows
5. Record any special-case UI modules:
   - `oeeDashboard.js`
   - `milestones.js`
   - `submissionModal.js`

## Tests that must pass
- App launches and renders categories without errors (baseline).
- Switching Budgetary/Final works (baseline).

## Success checklist
- [ ] Confirmed scroll root and category-group DOM.
- [ ] Confirmed where render is triggered in main.js.
- [ ] Noted any section modules that insert content post-render (OEE/Milestones).
