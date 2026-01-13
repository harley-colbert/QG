# planQuoteGenV4.7

Date: 2026-01-13 (America/Detroit)

Source repo snapshot: `QuoteGenV4.5.zip`

Objective: Remove all formatted-text inputs and eliminate *all* Quill dependencies (frontend + backend Word pipeline), while preserving the existing QuoteGen behavior and file contracts.

This plan is written for an **agent-based execution workflow** (Codex/agents). Each phase file contains:
- Scope and exact files touched
- Step-by-step tasks
- Tests that must pass
- A success checklist (phase exit criteria)

## What “done” means
1. No Quill assets, imports, or runtime references remain anywhere in the repo.
2. All formerly-rich fields are **plain text** inputs (`<textarea>`) and persist correctly.
3. Stored data is plain text; legacy HTML/Quill content is cleaned on load and on save.
4. Word generation inserts plain text (optionally preserving line breaks), with no HTML/Delta conversion.

## Where to start
- Read **Immutables** first: `immutables/IMMUTABLES.md`
- Then read **Contracts**: `contracts/CONTRACTS_INDEX.md`
- Execute phases in order: `phases/Phase00_Preflight.md` → `Phase05_Release_Audit.md`
