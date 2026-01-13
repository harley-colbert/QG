# Agent 05 — Release audit + packaging

## Primary objective
Run final audits, full smoke tests, and create the release artifact `QuoteGenV4.7.zip`.

## Inputs
- Plan phase: `phases/Phase05_Release_Audit.md`
- Global DoD:
  - `shared/DEFINITION_OF_DONE.md`

## Tasks (do in order)
1. Run audit scripts from repo root:
   - PowerShell: `.\tools\audit_no_quill.ps1`
   - Bash: `tools/audit_no_quill.sh`
   Both must PASS (zero prohibited hits).
2. Verify `models/headers.py` unchanged:
   - compare file hash to original (or diff must be empty)
3. Full smoke tests:
   - Budgetary: New → Fill multiline → Save → Open → Submit
   - Final: same flow (if used)
   - Dynamic sections: multiple entries survive save/open
4. Package:
   - Create `QuoteGenV4.7.zip` of the repo.
   - Ensure it does not contain deleted Quill files.

## Evidence to capture
- Audit PASS output
- Brief smoke test notes
- Confirmation of headers.py unchanged
- Final zip file name

## Exit criteria
- All Definition of Done items satisfied.
- Release zip produced.
