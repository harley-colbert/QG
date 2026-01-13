# Section Navigation Contract

New module: `views/web/js/sectionNav.js`

## Responsibilities
1. Build the sidebar list by scanning `.category-group` elements after a render.
2. Provide click-to-jump scrolling within `#scroll-container`.
3. Track active section using IntersectionObserver with:
   - `root: document.getElementById("scroll-container")`

## Inputs
- DOM: `.category-group` elements must exist.
- Each `.category-group` must have:
  - `id` (scroll target)
  - `data-category` (label text)

## Outputs
- Sidebar list under `#section-nav` populated with `.section-nav-item` elements.
- Active class toggled as user scrolls.

## Rebuild triggers
SectionNav must be rebuilt when:
- Quote type changes (budgetary/final)
- Categories re-render
- Dynamic sections add/remove a category group (if that exists)

Implementation rule:
- Expose `rebuildSectionNav()` and call it after render and after dynamic adds/removes (if applicable).

## Prohibited
- SectionNav must NOT own field values.
- SectionNav must NOT mutate viewStore.
