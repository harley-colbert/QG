# Form Layout Contract

Goal: improve scanning, reduce label wrapping, and optionally enable compact density.

## Required improvements (Phase 05 baseline)
- Labels must not wrap in awkward narrow columns next to inputs.
- Layout must remain functional in existing desktop window sizes.

## Allowed strategies
A) “Label above input” for all fields (simplest, most consistent).
B) Responsive grid:
   - desktop: 2 columns for short fields
   - mobile/narrow: 1 column
   - labels above each input within grid cells

## Density toggle (optional)
- Provide a compact mode via a CSS class on `body` or `#app-shell`.
- Compact mode reduces padding and input height.

## Prohibited
- Do not change field keys or input names.
- Do not change how viewStore finds controls (`name` / `data-field-key`).
