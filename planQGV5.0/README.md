# planQGV5.0

Date: 2026-01-13 (America/Detroit)

Source repo snapshot: `QuoteGenV4.7.zip`

## Objective
Implement an improved UI/UX structure for QuoteGen without a framework rewrite:

1. **Two-column shell**: left sidebar section index + right content.
2. **Section index**: click-to-jump + active section highlight while scrolling.
3. **Collapsible sections** (accordion): collapse/expand categories, persist state.
4. **System status visibility**: current file, dirty state, last-saved timestamp.
5. **Action feedback**: toast notifications for Save/Open/New/Submit + long-running Submit.
6. **Form readability**: reduce label-wrapping pain and improve scanning (CSS-driven).
7. **Optional**: completion badges / validation to show “what’s left”.

This plan is written for an agent-based execution workflow. Each phase includes:
- Exact file paths
- Step-by-step tasks
- Tests that must pass
- Success checklist (exit criteria)

## Start here
1. `immutables/IMMUTABLES.md`
2. `contracts/CONTRACTS_INDEX.md`
3. Execute phases in order:
   - `phases/Phase00_Preflight.md`
   - `phases/Phase01_AppShell_Layout.md`
   - `phases/Phase02_SectionNav.md`
   - `phases/Phase03_CollapsibleSections.md`
   - `phases/Phase04_Status_Toasts.md`
   - `phases/Phase05_Readability_Validation.md`
   - `phases/Phase06_Release_Audit.md`

## Definition of Done
See `tests/DEFINITION_OF_DONE.md`.
