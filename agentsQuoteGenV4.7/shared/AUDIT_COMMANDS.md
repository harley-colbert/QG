# Audit Commands (Global)

These commands are used throughout phases to confirm Quill removal.

## PowerShell (Windows)
From repo root:
- `powershell -ExecutionPolicy Bypass -File .\tools\audit_no_quill.ps1`

Expected:
- Exit code 0
- Prints: `PASSED: No Quill remnants found.`

## Bash (macOS/Linux)
From repo root:
- `bash tools/audit_no_quill.sh`

Expected:
- Exit code 0
- Prints: `PASSED: No Quill remnants found.`

## Manual grep (backup)
Search repo for:
- `quill`
- `ql-`
- `dangerouslyPasteHTML`
