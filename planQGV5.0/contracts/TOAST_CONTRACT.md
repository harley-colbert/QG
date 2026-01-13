# Toast Contract

New module: `views/web/js/toast.js`

## Responsibilities
- Provide user feedback without modal interruptions for:
  - Save success/failure
  - Open success/failure
  - Submit start/success/failure
  - Validation warnings (optional)

## API
Export these functions:
- `toastSuccess(message, opts?)`
- `toastError(message, opts?)`
- `toastInfo(message, opts?)`

## Behavior
- Toasts append to `#toast-container`.
- Default auto-dismiss after ~3–5 seconds (configurable).
- Error toasts remain longer or require dismiss (optional).

## Styling requirements
- Toasts must be readable (contrast).
- Must not cover the toolbar controls.
