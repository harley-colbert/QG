# Agent 00 — Preflight + Safety Nets

## Primary objective
Establish baseline and produce a definitive Quill touchpoint inventory before code changes.

## Inputs
- Source repo: `QuoteGenV4.5.zip` (unzipped to a working folder)
- Plan: `phases/Phase00_Preflight.md` (from plan zip)

## Tasks (do in order)
1. Run the app once (baseline) and confirm UI loads.
2. Search the repo for:
   - `quill`
   - `ql-`
   - `dangerouslyPasteHTML`
3. Record each match with:
   - file path
   - line(s)
   - category: frontend asset / frontend runtime / backend conversion / other
4. Ensure the plan’s audit scripts exist in `tools/`:
   - `tools/audit_no_quill.ps1`
   - `tools/audit_no_quill.sh`
   If they don’t exist, create them exactly as specified in the plan zip.

## Required outputs
- A “Quill touchpoint list” with exact paths and short notes (save into your phase log).

## Tests to run
- Baseline UI load (manual)
- Run the audit scripts (they will fail until Quill is removed, but must enumerate findings).

## Evidence to capture
- Audit output showing current Quill hits
- A short list of files that will be deleted/modified in Phase 01/02

## Exit criteria
- You have a complete inventory of Quill dependencies and usage locations.
- Audit scripts are runnable from repo root.
