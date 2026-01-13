// views/web/js/contactsModal.js

import {
  getAllianceContacts,
  deleteAllianceContact
} from './apiWrapper.js';
import {
  showEditContactModal,
  ensureEditContactModalLoaded
} from './editContactsModal.js';

const CONTACTS_HTML_PATH = 'admin/contacts.html';

function verboseLog(...args) {
  console.log('[ContactsModal]', ...args);
}

/**
 * Loads and displays the Contacts modal dialog.
 */
export async function loadContactsModal() {
  verboseLog('Opening contacts modal...');

  // Fetch the HTML template
  let resp, htmlText;
  try {
    resp = await fetch(CONTACTS_HTML_PATH);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    htmlText = await resp.text();
  } catch (err) {
    verboseLog('Could not fetch contacts.html:', err);
    alert('Error loading contacts modal. Please try again later.');
    return;
  }

  // Inject HTML into modal body
  const doc = new DOMParser().parseFromString(htmlText, 'text/html');
  const mainEl = doc.querySelector('main');
  const modalBody = document.getElementById('contacts-modal-body');
  if (!mainEl || !modalBody) {
    verboseLog('contacts-modal-body or <main> not found!');
    alert('Internal error: contacts modal could not be shown.');
    return;
  }
  modalBody.innerHTML = mainEl.innerHTML;

  // Show the modal
  const modal = document.getElementById('contacts-modal');
  modal.style.display = 'flex';

  // Wire up close buttons
  ['close-contacts', 'btn-close-contacts'].forEach(id => {
    const btn = document.getElementById(id);
    if (btn) btn.onclick = () => closeModal();
  });

  // Add Contact
  const addBtn = document.getElementById('add-contact');
  if (addBtn) {
    addBtn.onclick = async () => {
      await ensureEditContactModalLoaded();
      showEditContactModal(null, async () => { await refreshContactsTable(); });
    };
  }

  // Refresh Contacts
  const refreshBtn = document.getElementById('refresh-contacts');
  if (refreshBtn) {
    refreshBtn.onclick = async () => { await refreshContactsTable(); };
  }

  // Initial table fill
  await refreshContactsTable();
  verboseLog('Contacts modal displayed.');
}

/**
 * Refreshes the contacts table with current contact data.
 */
export async function refreshContactsTable() {
  verboseLog('Refreshing contacts table...');
  let contacts = [];
  try {
    contacts = await getAllianceContacts();
    verboseLog('Loaded contacts:', contacts);
  } catch (err) {
    verboseLog('Error loading contacts:', err);
    alert('Could not load contacts.');
    return;
  }

  const tbody = document.querySelector('#contacts-table tbody');
  if (!tbody) {
    verboseLog('No #contacts-table tbody found.');
    return;
  }
  tbody.innerHTML = '';

  contacts.forEach(c => {
    const tr = document.createElement('tr');
		tr.innerHTML = `
		  <td>${c.name}</td>
		  <td>${c.email || ''}</td>
		  <td>${c.phone || ''}</td>
		  <td>${c.title || ''}</td>
		  <td>
			<button class="action-btn edit" data-id="${c.id}">Edit</button>
			<button class="action-btn delete" data-id="${c.id}">Delete</button>
		  </td>`;
		tbody.appendChild(tr);
  });

  // Wire Edit buttons
  tbody.querySelectorAll('button.edit').forEach(btn => {
    btn.onclick = async () => {
      const contactId = btn.dataset.id;
      const contact = contacts.find(x => String(x.id) === String(contactId));
      if (!contact) {
        verboseLog(`No contact found for id=${contactId}`);
        return;
      }
      await ensureEditContactModalLoaded();
      showEditContactModal(contact, async () => { await refreshContactsTable(); });
    };
  });

  // Wire Delete buttons
  tbody.querySelectorAll('button.delete').forEach(btn => {
    btn.onclick = async () => {
      const contactId = btn.dataset.id;
      if (!confirm('Delete this contact?')) return;
      try {
        await deleteAllianceContact(Number(contactId));
        verboseLog('Deleted contact:', contactId);
      } catch (err) {
        verboseLog('Error deleting contact:', err);
        alert('Could not delete contact.');
      }
      await refreshContactsTable();
    };
  });
}

/**
 * Closes the contacts modal by hiding it.
 */
function closeModal() {
  const modal = document.getElementById('contacts-modal');
  if (modal) {
    modal.style.display = 'none';
    verboseLog('Contacts modal closed.');
  }
}
