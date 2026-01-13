# Immutables Summary (Agent Quick Reference)

This is a condensed reference. The source of truth is in:
- plan zip: `immutables/IMMUTABLES.md`

## Critical immutables
1. Do not modify `models/headers.py` (byte-for-byte).
2. Preserve field key namespace: `data.*` (including dynamic numeric suffixes).
3. Preserve XML root `<QuoteData>` and tag sanitizer rules.
4. Preserve user flows: New → Save → Open → Submit.
5. Eliminate Quill completely.
6. No HTML stored after refactor (sanitize on load/save).
