# App Shell DOM Contract

This contract defines the required DOM structure and IDs/classes used by new UI modules.

## Required elements (IDs)

### Layout
- `#app-shell` — root container for the shell layout
- `#app-sidebar` — left sidebar container
- `#app-main` — right main container (contains toolbar + scroll content)
- `#scroll-container` — the single scroll root for category content
  - MUST be the scroll root used by SectionNav IntersectionObserver

### Sidebar
- `#section-nav` — list container for section links
- `#section-nav-search` — optional input for filtering sections (Phase 05 optional)
- `.section-nav-item` — clickable section nav row
- `.section-nav-item.active` — indicates current section in view

### Status (Toolbar area)
- `#status-file` — shows current open file (or “Unsaved”)
- `#status-dirty` — shows dirty indicator (e.g., ● Unsaved changes)
- `#status-last-saved` — shows last saved timestamp

### Toasts
- `#toast-container` — container for toast notifications

## Category group requirements
Category group blocks MUST include:
- `.category-group` — wrapper
- `data-category="<CategoryTitle>"` — stable identifier for nav + collapse state
- An `id` used for scrolling (e.g., `id="cat-<slug>"`)

## Non-goals
- This contract does not require reworking how fields are generated.
- It wraps/enhances the existing structure.
