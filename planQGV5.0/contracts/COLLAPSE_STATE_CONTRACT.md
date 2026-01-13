# Collapse State Contract

New behavior: each category group is collapsible.

## Required UI behavior
- Clicking the category header toggles collapsed state.
- Collapsed state hides the fields container (but keeps DOM to preserve values).
- Collapsed state persists across:
  - rerenders
  - quote type switching
  - app restart

## Storage key
- Use localStorage key: `qg.collapse.<quoteType>.<categorySlug>`
  - quoteType: `budgetary` or `final`
  - categorySlug: stable slug of `data-category` text

## DOM hooks
- `.category-group` receives class `.collapsed` when collapsed.
- The fields wrapper is `.fields-container` (or whatever exists) and is hidden when collapsed.

## Default state
- Default: expanded
- Optional enhancement: “Collapse all / Expand all” controls in sidebar

## Prohibited
- Collapsing must not unregister fields or lose values.
