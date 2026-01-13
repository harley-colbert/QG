# Phase 05 — Form readability + optional completion/validation

## Purpose
Improve form scanability and optionally show “what’s left” via section completion badges.

## Contracts referenced
- `contracts/FORM_LAYOUT_CONTRACT.md`
- `contracts/SECTION_NAV_CONTRACT.md`

## Files to add (optional)
- `views/web/js/validation.js` (if implementing completion badges)

## Files to modify
- `views/web/styles.css`
- `views/web/js/main.js` (only if adding completion badges)
- `views/web/js/sectionNav.js` (only if completion status displayed in nav)

## Step-by-step tasks

### 1) Improve form layout (required)
In CSS:
- Move to label-above-input layout OR a responsive grid.
- Ensure it does not break existing field generation.
- Ensure file-picker rows still align.

### 2) Optional: add compact density toggle
- Add a toggle button in toolbar (e.g., “Compact”)
- Toggle a class on `body` or `#app-shell`
- Compact CSS reduces padding and input height.

### 3) Optional: completion badges per section
Implement `validation.js`:
- `computeSectionCompletion(categoryEl)` returns:
  - complete boolean
  - missingCount
- Update sidebar rows with:
  - ✓ for complete
  - numeric badge for missing
Trigger recalculation:
- after render
- on input change (debounced)

Important:
- Do not block typing; debounce validation updates.

## Tests that must pass
1. Labels no longer wrap awkwardly; scanning improves.
2. Inputs remain accessible and usable.
3. Optional: completion badges update live and match reality.

## Success checklist
- [ ] Form readability improved without regressions.
- [ ] Optional enhancements behave correctly and don’t slow UI.
