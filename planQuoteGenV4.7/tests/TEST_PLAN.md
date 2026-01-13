# Test Plan (Global)

This file summarizes the minimum validation needed across all phases.
Each phase file also contains phase-specific tests and exit criteria.

## Required checks
1. UI loads without console errors.
2. New Quote → Save XML → Open XML works for both quote types (if both are used).
3. Dynamic categories with “Add” continue to behave correctly:
   - multiple entries
   - save/open repopulates
4. Word export works:
   - no runtime errors
   - plain text content
   - multiline values preserved in a readable way
5. Audit: no Quill remnants remain.

## Recommended regression checks
- Spell check categories still functions (if used)
- Special list dropdowns still behave (ID + name2 fields)
- Numeric fields still normalize correctly (%, $)
