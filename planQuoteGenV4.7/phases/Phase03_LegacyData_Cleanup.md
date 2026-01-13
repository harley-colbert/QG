# Phase 03 — Legacy Data Cleanup (Old XML content that contains HTML)

## Purpose
Ensure opening older XML files (previously saved with Quill HTML) produces readable plain text in the UI and does not re-save HTML.

## Contracts referenced
- `contracts/TEXT_SANITIZATION_CONTRACT.md`
- `contracts/JS_API_CONTRACT.md`
- `immutables/IMMUTABLES.md` (I3, I6)

## Files to modify (exact paths)
- `models/quote_model.py` (load path) OR `viewmodels/quote_viewmodel.py` (load-to-UI path)

## Implementation decision (choose one and document it)
Option A — Normalize at load time in the model:
- After `load_from_xml()`, traverse stored strings and strip markup.

Option B — Normalize when exposing to UI in ViewModel:
- When computing the `fields` map returned to JS, sanitize values.

Either option is acceptable, but it must satisfy:
- UI never shows raw HTML tags
- Re-saving does not reintroduce HTML

## Step-by-step tasks
1. Implement a recursive traversal for loaded data:
   - If value is string: sanitize to plain text
   - If dict: recurse
2. Preserve paragraph intent:
   - Convert `<br>` and paragraph boundaries to newlines prior to stripping tags
3. Ensure the “save” path uses the same sanitizer so that:
   - even if HTML slips in from somewhere, it is removed before XML is written.

## Tests that must pass
1. Take an old XML known to contain `<p>` / `<br>` content.
2. Open it:
   - UI shows plain text with correct line breaks
3. Save it again:
   - The new XML should contain no `<` `>` tag sequences in field values (spot-check).

## Success checklist
- [ ] Opening legacy XML yields plain text in the UI.
- [ ] Saving legacy XML produces plain text values only.
