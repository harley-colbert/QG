# Agent 01 — App Shell layout (sidebar + main) + single scroll

## Objective
Implement the two-column shell with required IDs and keep the app functional.

## Files to modify
- `views/web/index.html`
- `views/web/styles.css`

## Tasks (strict order)
1. Update `index.html`:
   - Wrap app in `#app-shell` with `#app-sidebar` + `#app-main`
   - Add `#section-nav` inside sidebar
   - Ensure `#scroll-container` exists and is inside main
   - Add `#toast-container`
2. Update CSS:
   - Implement sidebar width + main flex
   - Ensure only `#scroll-container` scrolls
   - Do NOT break existing toolbar layout
3. Verify that all existing element IDs referenced by JS still exist (do not rename).

## Tests
1. Launch app: no errors
2. Switch quote type: works
3. Scroll: works
4. Open Contacts and Settings modals: still work

## Evidence
- Screenshot: new layout visible with sidebar empty and content on right
- Console: no errors

## Exit criteria
- Layout exists and nothing else broke.
