# Text Sanitization Contract (Plain-text canonicalization)

Objective: Ensure all user-editable description content is plain text across:
- DOM inputs
- ViewStore snapshots
- XML persistence
- Word generation

## Canonical representation
- Values are stored as **plain Unicode text**.
- Newlines are stored as `\n` (LF). (CRLF may be accepted from the OS but must normalize to LF for storage.)

## Sanitization rules (MUST)
Whenever a value enters the backend (set_field / set_all_fields / save_quote):
1. If value is not a string, coerce to string safely (or reject with logging).
2. Convert CRLF (`\r\n`) and CR (`\r`) to LF (`\n`).
3. If value contains HTML markup, strip tags to plain text.
   - Preserve line breaks where reasonable:
     - `<br>` -> `\n`
     - block tags like `</p><p>` should yield `\n`
4. Trim only *trailing* whitespace on each line if needed (optional), but do NOT collapse meaningful spacing.

## Legacy data cleanup (MUST)
When loading XML into the model:
- Any string that appears to contain HTML must be normalized using the same rules above.
- After “Open Quote”, the frontend should see readable plain text (not raw `<p>...</p>`).

## Prohibited
- Storing HTML in any field
- Storing Quill Delta JSON as canonical field content
