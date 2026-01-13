// js/quillSetup.js
// -----------------------------------------------------------------------------
// Central Quill configuration + helpers.
// Every editor is registered globally via registerQuill so saveViewStore() can
// capture its HTML without hitting undefined.
// -----------------------------------------------------------------------------

import Quill from 'quill';
import { registerQuill } from './viewStore.js';   // ← global store

/**
 * Shared configuration for every Quill editor.
 * Adjust toolbar items or theme as needed.
 */
export const quillOptions = {
  theme: 'snow',
  placeholder: 'Type here…',
  modules: {
    toolbar: {
      container: [
        // Headings
        [{ header: [1, 2, 3, false] }],

        // Inline formatting
        ['bold', 'italic', 'underline', 'strike'],

        // Lists & indentation
        [{ list: 'ordered' }, { list: 'bullet' }],
        [{ indent: '-1' }, { indent: '+1' }],

        // Alignment
        [{ align: [] }],

        // Color pickers
        [{ color: [] }, { background: [] }],

        // Links, images, code, blockquote
        ['link', 'image', 'code-block', 'blockquote'],

        // Remove formatting
        ['clean']
      ]
      // Add custom handlers if needed
    },

    // Undo/redo stack (1 s debounce, 200 actions)
    history: {
      delay: 1000,
      maxStack: 200,
      userOnly: true
    },

    // Keep pasted HTML intact
    clipboard: {
      matchVisual: false
    }
  }
};

/**
 * Internal registry (optional utility).  Do not rely on this for save logic;
 * saveViewStore iterates quillInstances from viewStore.js.
 */
const instances = {};

/**
 * Create a Quill editor, optionally pre‑seed HTML, and make it discoverable.
 *
 * @param {string}       fieldKey      e.g. "data.systemDescription.1"
 * @param {HTMLElement}  containerDiv  <div> the editor mounts in
 * @param {string=}      initialHTML   starting HTML (optional)
 * @returns {Quill}
 */
export function initQuill(fieldKey, containerDiv, initialHTML = '') {
  if (typeof Quill === 'undefined') {
    console.error('❌ Quill not found! Make sure quill.js is loaded.');
    return;
  }

  const quill = new Quill(containerDiv, quillOptions);

  // Preload content if provided
  if (initialHTML) {
    quill.clipboard.dangerouslyPasteHTML(initialHTML, 'silent');
  }

  // Optional grammar/spell attributes
  quill.root.setAttribute('data-gramm', 'true');
  quill.root.setAttribute('data-gramm_editor', 'true');

  // Mirror changes into hidden <input name="{fieldKey}"> and backend
  quill.on('text-change', () => {
    const html = quill.root.innerHTML;

    const hidden = document.querySelector(`input[name="${fieldKey}"]`);
    if (hidden) hidden.value = html;

    window.pywebview?.api
      .set_field(fieldKey, html)
      .catch(err => console.error('Error setting field', fieldKey, err));
  });

  // ★ Register in the global store so saveViewStore can find it
  registerQuill(fieldKey, quill);

  // Keep local copy for rehydrate convenience
  instances[fieldKey] = quill;
  return quill;
}

/**
 * Rehydrate existing editors with HTML (e.g., when switching quote types).
 * @param {Record<string,string>} data
 */
export function rehydrateQuills(data = {}) {
  Object.entries(instances).forEach(([key, quill]) => {
    const html = data[key] || '';
    const delta = quill.clipboard.convert(html);
    quill.setContents(delta, 'api');
  });
}

/**
 * Optional: expose all live instances for debugging.
 */
export function getQuillInstances() {
  return { ...instances };
}
