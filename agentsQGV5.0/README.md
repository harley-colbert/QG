# agentsQGV5.0

Date: 2026-01-13 (America/Detroit)

Pairs with: `planQGV5.0.zip`
Source repo snapshot: `QuoteGenV4.7.zip`

These agent files are designed to execute the plan phases in `planQGV5.0.zip`.

## Execution order
1. Read and obey:
   - Plan immutables: `immutables/IMMUTABLES.md`
   - Contracts index: `contracts/CONTRACTS_INDEX.md`
2. Execute agents in order:
   - `agents/Agent00_Preflight.md`
   - `agents/Agent01_AppShell_Layout.md`
   - `agents/Agent02_SectionNav.md`
   - `agents/Agent03_CollapsibleSections.md`
   - `agents/Agent04_Status_Toasts.md`
   - `agents/Agent05_Readability_Validation.md`
   - `agents/Agent06_Release_Audit.md`

## Deliverable
- Updated repo packaged as: `QuoteGenV5.0.zip`
- All tests and definition-of-done checks pass.
