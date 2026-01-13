# Phase 02 — Backend: Remove Quill/HTML Word conversion; export plain text only

## Purpose
Delete Quill conversion modules and refactor Word generation to treat all fields as plain text.

## Contracts referenced
- `contracts/WORD_EXPORT_CONTRACT.md`
- `contracts/TEXT_SANITIZATION_CONTRACT.md`
- `immutables/IMMUTABLES.md` (I3, I6, I7)

## Files to delete (exact paths)
- `services/quill_to_word.py`
- `utilities/quill_lists.py`
- `services/word/quill_convert.py`
- `services/word/html_shim.py`
- `services/word/test_quill_delta.py`

## Files to modify (exact paths)
- `services/word/handler.py`
- `services/word/sanitize.py`
- `services/word/constants.py`

## Step-by-step tasks

### 1) Remove imports and references to Quill conversion
In `services/word/handler.py`:
- Remove imports of any module that exists solely for HTML/Quill conversion.
- Replace any “HTML -> docx” or “Delta -> docx” path with a plain-text path.

### 2) Implement “plain text multiline” handling
In `services/word/handler.py`:
- When encountering a string containing `\n`, render as:
  - multiple Word paragraphs, one per line (preferred for readability), OR
  - a single paragraph with line breaks
- Keep behavior consistent across all fields.

### 3) Replace sanitization strategy
In `services/word/sanitize.py`:
- Ensure sanitization always strips markup to text (no exceptions list for “rich fields”).
- Add helpers that:
  - convert `<br>` and paragraph boundaries to newlines before stripping tags.

In `services/word/constants.py`:
- Remove any constants that exist only to support “HTML exceptions”.
- Rename any Quill-specific logging prefixes to neutral ones.

## Tests that must pass
1. Generate Word output from a quote containing:
   - multi-line text (with `\n`)
   - pasted HTML-like content (e.g., `<b>bold</b><br>next line`)
2. Verify the Word document:
   - Contains no literal HTML tags
   - Preserves intended line breaks
   - Does not throw errors during generation
3. Run unit tests under `services/word/` (if they exist and are runnable in your environment).

## Success checklist
- [ ] No backend Quill/HTML conversion modules remain.
- [ ] Word export is plain text only.
- [ ] Sanitization prevents HTML artifacts from leaking into the Word output.
