# agentsQuoteGenV4.7

Date: 2026-01-13 (America/Detroit)

Pairs with: `planQuoteGenV4.7.zip`
Source repo snapshot: `QuoteGenV4.5.zip`

These agent files are designed to execute the plan phases in `planQuoteGenV4.7.zip`.
They assume an “agent mode” workflow where:
- The agent can edit files in the unzipped repo
- The agent can run the app locally (manual smoke tests)
- The agent can run the audit scripts under `tools/`

## Non-negotiables
- `models/headers.py` must remain byte-for-byte identical.
- Quill must be removed completely (assets + imports + backend conversion).
- All fields become plain text (textarea), and Word export is plain text only.

## Recommended workflow
1. Unzip the source repo (`QuoteGenV4.5.zip`) to a working directory.
2. Unzip the plan zip (`planQuoteGenV4.7.zip`) and read:
   - `immutables/IMMUTABLES.md`
   - `contracts/CONTRACTS_INDEX.md`
3. Execute phases in order:
   - `agents/Agent00_Preflight.md`
   - `agents/Agent01_Frontend_RemoveQuill.md`
   - `agents/Agent02_Backend_WordPlainText.md`
   - `agents/Agent03_LegacyDataCleanup.md`
   - `agents/Agent04_FieldMapFlattenFix.md`
   - `agents/Agent05_Release_Audit.md`
4. Produce a final release zip:
   - `QuoteGenV4.7.zip`

## Required deliverables
- Updated repo content meeting the plan requirements
- Audit scripts pass (no Quill remnants)
- End-to-end smoke tests pass
- Final `QuoteGenV4.7.zip` artifact

## Logging & evidence
Each agent phase has a “Evidence to capture” section. Save the evidence to:
- `agent_logs/PhaseXX_*.md` (suggested) in your working copy (not required, but strongly recommended)
