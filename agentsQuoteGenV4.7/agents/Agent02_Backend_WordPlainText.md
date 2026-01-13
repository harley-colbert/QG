# Agent 02 — Backend: Remove Quill/HTML conversion and export plain text

## Primary objective
Remove backend Quill/HTML-to-Word conversion pipeline and ensure Word export is plain text only.

## Inputs
- Plan phase: `phases/Phase02_Backend_RemoveQuill_WordPlainText.md`
- Contracts:
  - `contracts/WORD_EXPORT_CONTRACT.md`
  - `contracts/TEXT_SANITIZATION_CONTRACT.md`

## Files to delete (verify and delete)
- `services/quill_to_word.py`
- `utilities/quill_lists.py`
- `services/word/quill_convert.py`
- `services/word/html_shim.py`
- `services/word/test_quill_delta.py`

## Files to modify
- `services/word/handler.py`
- `services/word/sanitize.py`
- `services/word/constants.py`

## Implementation guidance (strict)
1. No HTML formatting reintroduction:
   - sanitize to plain text
   - do not create lists/bold/italics
2. Multiline handling:
   - `\n` should become readable paragraphs or line breaks
3. Rename Quill-specific logs:
   - Replace `[QUILL2DOC]` with `[WORD]` or similar

## Tests to run (must)
1. Create a quote with:
   - multiline description
   - pasted text that includes `<b>`, `<p>`, `<br>`
2. Submit to Word:
   - must generate successfully
   - output must contain no literal tags
   - multiline must be readable

## Evidence to capture
- Word generation success output/log
- Notes on how multiline is preserved (paragraph-per-line vs line breaks)

## Exit criteria
- Word export is plain text only and stable.
- No backend conversion modules remain.
