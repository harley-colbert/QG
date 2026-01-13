# Contracts Summary (Agent Quick Reference)

This is a condensed reference. The source of truth is in:
- plan zip: `contracts/`

## Key contract points

### JS API
- `open_quote()` must return `{ quoteType, quotes, fields }`
- `fields` must be a flat dict: `fieldKey -> string`

### ViewStore
- Flat map store: `viewStore[type][fieldKey] = string`
- Controls are found by `[data-field-key]` or `[name]`
- No Quill instance tracking exists after refactor

### Sanitization
- Normalize CRLF -> LF
- Convert `<br>` / paragraph boundaries to `\n` before stripping tags
- Strip all HTML to plain text
- Never store HTML or Delta JSON

### Word export
- Plain text only
- Preserve multiline
- No HTML/Delta conversion modules
