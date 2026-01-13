# ViewStore Contract (Frontend field store)

Source file (reference): `views/web/js/viewStore.js`

## Canonical store shape
The frontend maintains an in-memory store:

- `viewStore["budgetary"]`: object mapping fieldKey -> string
- `viewStore["final"]`: object mapping fieldKey -> string

## Field key rules
- Field keys must be strings.
- Field keys for quote data MUST start with `data.`.
- Static keys resemble:
  - `data.CustomerContactInformation.customerName`
- Dynamic keys use numeric suffixes:
  - `data.MajorEquipment.EquipmentDescription.0`
  - `data.MajorEquipment.EquipmentDescription.1`

## Apply behavior
When applying a store snapshot to the DOM:
- For each key/value pair, the UI finds the corresponding element via:
  - `[data-field-key="<fieldKey>"]` OR `[name="<fieldKey>"]`
- The element’s `.value` becomes the stored string.

## Save behavior
When saving a snapshot from DOM controls:
- `activeFieldKeys` defines which fields must be captured.
- For inputs, selects, and textareas: snapshot stores `.value` as string.
- For any “special lists” or numeric formatting rules already present, behavior remains unchanged.

## Quill removal rule (new)
After this refactor:
- There are **no Quill instances**.
- The store contains **only plain text values**.
- No HTML is stored in viewStore.

## Backend alignment (required)
The backend API method `get_all_fields()` must return the same flat mapping shape that viewStore expects.
