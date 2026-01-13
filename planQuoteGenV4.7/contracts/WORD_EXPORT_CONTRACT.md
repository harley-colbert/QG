# Word Export Contract (Plain text only)

Source files (reference):
- `services/word/handler.py`
- `services/word/sanitize.py`
- `services/word/constants.py`

## Required behavior
1. Word generation inserts **plain text** for every field.
2. No HTML or Quill Delta conversion occurs.
3. Multiline text is preserved:
   - Either as separate paragraphs per line
   - Or as line breaks inside a paragraph (implementation choice)
4. Word generation must not throw on strings containing `<` `>` or legacy HTML; it must treat them as text after sanitization.

## Template contract
- Existing templates remain valid.
- Placeholder keys remain unchanged.
- If the template pipeline currently expects subdocs for “rich” fields, it must now accept “plain text subdocs” (multi-paragraph) or raw strings.

## Prohibited
- Any dependency on Quill conversion functions/modules
- Any HTML parser that reintroduces formatting (bold, lists, etc.)
