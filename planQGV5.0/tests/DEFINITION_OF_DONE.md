# Definition of Done

The UI/UX upgrade is complete only if all items below are true:

## UI structure
- [ ] App uses a 2-column shell (sidebar + main content).
- [ ] Sidebar lists all rendered sections.
- [ ] Clicking a section scrolls within the app to that section.
- [ ] Active section highlights while scrolling.

## Usability
- [ ] Sections can be collapsed/expanded.
- [ ] Collapse state persists across rerenders and restarts.

## System status
- [ ] Toolbar shows current file (or “Unsaved”).
- [ ] Dirty indicator appears after edits.
- [ ] Last saved timestamp updates on save.

## Feedback
- [ ] Save/Open/New/Submit show toast feedback.
- [ ] Submit shows progress/spinner and disables Submit while running.

## No regressions
- [ ] Contacts modal works.
- [ ] Settings modal works.
- [ ] Submission modal works.
- [ ] Dynamic sections still work and preserve values.
- [ ] Save/Open/Submit flows still work for both Budgetary and Final.

## Accessibility
- [ ] Keyboard tab order still works.
- [ ] Visible focus outlines remain.
