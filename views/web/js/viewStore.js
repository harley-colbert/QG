// viewStore.js
// Centralised data stores and active field registry

/**
 * Flat, per‑quote‑type cache of fieldKey → string.
 */
export const viewStore = {
  budgetary: {},
  final: {}
};

/**
 * Registered active field keys (inputs, selects, textareas, Quill editors).
 */
export const activeFieldKeys = new Set();

/**
 * Map of Quill editors keyed by fieldKey.
 */
export const quillInstances = {};

/**
 * Register a field so saveViewStore knows to include it.
 * @param {string} fieldKey
 */
export function registerField(fieldKey) {
  activeFieldKeys.add(fieldKey);
}

/**
 * Unregister a field when it’s removed from the DOM.
 * Also cleans up stored values.
 * @param {string} fieldKey
 */
export function unregisterField(fieldKey) {
  activeFieldKeys.delete(fieldKey);
  // Remove any saved snapshot
  Object.keys(viewStore).forEach(type => {
    delete viewStore[type][fieldKey];
  });
  // Also unregister Quill if present
  if (quillInstances[fieldKey]) delete quillInstances[fieldKey];
}

/**
 * Link a newly created Quill editor to its fieldKey and register it.
 * @param {string} fieldKey
 * @param {Quill} quill
 */
export function registerQuill(fieldKey, quill) {
  quillInstances[fieldKey] = quill;
  registerField(fieldKey);
}

/**
 * Unregister a Quill editor when its field is removed.
 * @param {string} fieldKey
 */
export function unregisterQuill(fieldKey) {
  delete quillInstances[fieldKey];
  unregisterField(fieldKey);
}

/**
 * Apply stored values back into the form.
 * @param {string} type – "budgetary" or "final"
 */
export function applyViewStore(type) {
  const data = viewStore[type] || {};
  // plain form controls
  Object.entries(data).forEach(([fieldKey, val]) => {
    const el =
      document.querySelector(`[data-field-key="${fieldKey}"]`) ||
      document.querySelector(`[name="${fieldKey}"]`);
    if (el && !(el.tagName === 'DIV' && quillInstances[fieldKey])) {
      el.value = val;
    }
  });
  // Quill editors
  Object.entries(quillInstances).forEach(([fieldKey, quill]) => {
    if (data[fieldKey] != null) {
      quill.clipboard.dangerouslyPasteHTML(data[fieldKey], 'silent');
    }
  });
}

/**
 * Snapshot all active fields (and OEE cards + Quills) into viewStore.
 * @param {string} type
 */
/**
 * Snapshot all active fields (and OEE cards + Quills) into viewStore.
 * @param {string} type
 */
export function saveViewStore(type) {
  // Create a fresh snapshot object
  const snapshot = {};

  // A) Named form controls for registered fields
  activeFieldKeys.forEach(fieldKey => {
	// Find the element by fieldKey (first by data-field-key, then by name)
	const el =
	  document.querySelector(`[data-field-key="${fieldKey}"]`) ||
	  document.querySelector(`[name="${fieldKey}"]`);
	if (!el) return;

	// Handle <select> elements: save value (ID) and text (name2)
	if (el.tagName === 'SELECT') {
	  // Save the selected value (ID/index)
	  snapshot[fieldKey] = el.value ?? '';
	  // Also store the selected label as fieldKey.name2
	  const selectedOption = el.selectedOptions && el.selectedOptions[0];
	  if (selectedOption) {
		snapshot[`${fieldKey}.name2`] = selectedOption.textContent.trim();
	  } else {
		snapshot[`${fieldKey}.name2`] = '';
	  }
	}
	// Handle input and textarea elements
	else if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
	  snapshot[fieldKey] = el.value ?? '';
	}
	// Do NOT set .name2 for other field types.
  });

  // B) OEE stat blocks (robust: supports id OR data-field-key, and varied markup)
	document.querySelectorAll('.oee-card, [data-field-key^="data.oee."]').forEach(node => {
	  // Prefer an explicit data-field-key; fall back to id
	  const key = node.dataset.fieldKey || node.id;
	  if (!key) return;

	  // Value may live in a .big span, in a [data-oee-value] node, or on the node itself
	  const valueNode = node.querySelector('.big, [data-oee-value]') || node;
	  let val = (valueNode.textContent || '').trim();

	  // Normalize common UI decorations
	  if (val.endsWith('%')) val = val.slice(0, -1).trim();

	  snapshot[key] = val;
	});

  // C) Quill editors
  Object.entries(quillInstances).forEach(([fieldKey, quill]) => {
	if (!quill || !quill.root) return;
	// Store HTML contents for this Quill field
	snapshot[fieldKey] = quill.root.innerHTML;
  });

  // Store the snapshot in the appropriate viewStore section
  viewStore[type] = snapshot;
}
