// views/web/js/settingsModal.js

import {
  browseTemplateFile,
  browseDbFolder,
  browseLogFolder,
  getAppSettings,
  updateAppSettings
} from './apiWrapper.js';

const SETTINGS_HTML_PATH = 'admin/settings.html';

function verboseLog(...args) {
  console.log('[SettingsModal]', ...args);
}

/**
 * Injects the settings HTML and wires up all controls and event handlers.
 * Loads settings from backend and populates all fields.
 */
export async function loadSettingsModal() {
  verboseLog('Opening settings modal...');

  // Fetch the HTML template
  let resp, htmlText;
  try {
    resp = await fetch(SETTINGS_HTML_PATH);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    htmlText = await resp.text();
  } catch (err) {
    verboseLog('Could not fetch settings.html:', err);
    alert('Error loading settings modal. Please try again later.');
    return;
  }

  // Inject HTML into modal body
  const doc = new DOMParser().parseFromString(htmlText, 'text/html');
  const mainEl = doc.querySelector('main');
  const settingsBody = document.getElementById('settings-modal-body');
  if (!mainEl || !settingsBody) {
    verboseLog('Modal target or source main not found!');
    alert('Internal error: settings modal could not be shown.');
    return;
  }
  settingsBody.innerHTML = mainEl.innerHTML;

  // Fetch settings from backend and populate fields
  try {
    const settings = await getAppSettings();
    populateSettingsForm(settings);
    verboseLog('Populated form from backend settings:', settings);
  } catch (err) {
    verboseLog('Could not load settings from backend:', err);
    alert('Failed to load settings. Please check your connection.');
  }

  // Wire Browse buttons (new IDs)
  wireBrowseButton('settings-browse-template', 'settings-template-filename', browseTemplateFile);
  wireBrowseButton('settings-browse-db-folder', 'settings-db-folder-path', browseDbFolder);
  wireBrowseButton('settings-browse-log-folder', 'settings-log-folder-path', browseLogFolder);

  // Wire Save (form submit)
  const settingsForm = document.getElementById('settings-form');
  if (settingsForm) {
    settingsForm.addEventListener('submit', async e => {
      e.preventDefault();
      verboseLog('Settings form submit triggered.');
      const newSettings = collectSettingsForm();
      try {
        await updateAppSettings(newSettings);
        verboseLog('Settings successfully updated:', newSettings);
        closeModal();
        alert('Settings saved.');
      } catch (err) {
        verboseLog('Failed to save settings:', err);
        alert('Error saving settings. Please try again.');
      }
    });
  } else {
    verboseLog('No #settings-form found.');
  }

  // Wire Cancel button (new ID)
  const cancelBtn = document.getElementById('settings-cancel-settings');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', closeModal);
  } else {
    verboseLog('No #settings-cancel-settings button found.');
  }
}

/**
 * Populate settings form fields based on the provided settings object.
 * Each form input's "name" attribute is used as the settings key.
 */
export function populateSettingsForm(settings = {}) {
  verboseLog('Populating settings form with:', settings);
  // Find all fields that have a name matching a settings key
  Object.keys(settings).forEach(key => {
    const field = document.querySelector(`[name="${key}"]`);
    if (field) {
      field.value = settings[key] !== undefined ? settings[key] : '';
      verboseLog(`Field "${key}" populated with:`, field.value);
    } else {
      verboseLog(`No input for settings key: ${key}`);
    }
  });
}

/**
 * Collects settings from all form fields with a "name" attribute.
 * Returns an object matching the backend settings shape.
 */
function collectSettingsForm() {
  const form = document.getElementById('settings-form');
  const formData = new FormData(form);
  const settings = {};
  for (const [key, value] of formData.entries()) {
    settings[key] = value.trim();
  }
  verboseLog('Collected form data:', settings);
  return settings;
}

/**
 * Wires up a browse button for a field with the provided IDs and API callback.
 */
function wireBrowseButton(buttonId, inputId, browseFn) {
  const button = document.getElementById(buttonId);
  const input = document.getElementById(inputId);
  if (!button || !input) {
    verboseLog(`Browse button or input missing: #${buttonId}, #${inputId}`);
    return;
  }
  button.addEventListener('click', async () => {
    verboseLog(`Browse button "${buttonId}" clicked.`);
    try {
      const result = await browseFn();
      if (result) {
        input.value = result;
        verboseLog(`Input "${inputId}" set to:`, result);
      }
    } catch (err) {
      verboseLog(`Browse failed for "${buttonId}":`, err);
      alert('Could not browse for this setting.');
    }
  });
}

/**
 * Closes the settings modal by hiding its parent element.
 */
function closeModal() {
  const modal = document.getElementById('settings-modal');
  if (modal) {
    modal.style.display = 'none';
    verboseLog('Settings modal closed.');
  }
}
