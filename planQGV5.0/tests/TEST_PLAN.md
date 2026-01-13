# Test Plan (Global)

## Manual smoke tests (must)
1. Launch app
   - UI loads without console errors
2. Budgetary flow
   - New → fill a few sections (including multiline textareas) → Save → Open → Submit
3. Final flow
   - Repeat above
4. Collapse persistence
   - Collapse 3 sections → restart app → verify same sections collapsed
5. Sidebar navigation
   - Click several nav items → scroll to correct sections
   - Scroll manually → active highlight updates
6. Dirty status
   - After Open: dirty off
   - Edit any field: dirty on
   - Save: dirty off + last saved updated
7. Modals
   - Manage Contacts opens and works
   - Manage Settings opens and works
   - Submit modal still displays results/errors

## Dev console checks (must)
- No uncaught exceptions during:
  - quote type switching
  - rendering categories
  - adding dynamic sections
  - saving/opening
