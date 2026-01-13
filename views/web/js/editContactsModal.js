// views/web/js/editContactsModal.js

import {
  addAllianceContact,
  updateAllianceContact
} from './apiWrapper.js';

const EDIT_CONTACTS_HTML_PATH = 'admin/editContacts.html';

let onSaveCallback = null;

/**
 * Ensures editContacts.html is loaded into the modal.
 */
export async function ensureEditContactModalLoaded() {
  const modalBody = document.getElementById('edit-contacts-modal-body');
  if (modalBody && !modalBody.innerHTML.trim()) {
    // Only fetch if not already loaded
    let resp, htmlText;
    try {
      resp = await fetch(EDIT_CONTACTS_HTML_PATH);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      htmlText = await resp.text();
    } catch (err) {
      alert('Error loading edit contact modal.');
      throw err;
    }
    const doc = new DOMParser().parseFromString(htmlText, 'text/html');
    const mainEl = doc.querySelector('main');
    if (!mainEl) throw new Error('editContacts.html missing <main>');
    modalBody.innerHTML = mainEl.innerHTML;
  }
}

/**
 * Shows the edit/add modal, optionally with contact data, wires up buttons.
 */
export function showEditContactModal(contact, onSave) {
  onSaveCallback = onSave || null;

  const modal = document.getElementById('edit-contacts-modal');
  const modalBody = document.getElementById('edit-contacts-modal-body');
  modal.style.display = 'flex';

  // Set modal title
  const title = document.getElementById('modal-title');
  title.textContent = contact && contact.id ? 'Edit Contact' : 'Add Contact';

  // Fill form fields
  document.getElementById('contact-id').value = contact?.id || '';
  document.getElementById('contact-name').value = contact?.name || '';
  document.getElementById('contact-title').value = contact?.title || '';
  document.getElementById('contact-cell').value = contact?.phone || '';
  document.getElementById('contact-email').value = contact?.email || '';

  // Save button
  document.getElementById('save-contact').onclick = async () => {
    const data = {
      id: document.getElementById('contact-id').value,
      name: document.getElementById('contact-name').value.trim(),
      title: document.getElementById('contact-title').value.trim(),
      phone: document.getElementById('contact-cell').value.trim(),
      email: document.getElementById('contact-email').value.trim(),
    };

    try {
      if (data.id) {
        await updateAllianceContact(data);
      } else {
        await addAllianceContact(data);
      }
      closeEditModal();
      if (onSaveCallback) await onSaveCallback();
    } catch (err) {
      alert('Failed to save contact.');
    }
  };

  // Cancel/close buttons
  document.getElementById('close-edit-contact').onclick =
    document.getElementById('cancel-edit-contact').onclick =
      () => closeEditModal();
}

/**
 * Hide the edit modal.
 */
function closeEditModal() {
  const modal = document.getElementById('edit-contacts-modal');
  if (modal) modal.style.display = 'none';
}
