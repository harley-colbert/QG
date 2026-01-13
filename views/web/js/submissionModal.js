// js/submissionModal.js

import {
  getAppSettings,
  browseTemplateFile,
  browseSaveFile
} from './apiWrapper.js';

const SUBMISSION_HTML_PATH = 'admin/submission.html';
let submissionModalLoaded = false;

/**
 * Loads and displays the submission modal.
 * Dynamically fetches, injects, and wires everything.
 * All actions are logged.
 */
export async function loadSubmissionModal() {
  console.log('[submissionModal] loadSubmissionModal() invoked');
  try {
    if (!submissionModalLoaded) {
      console.log(`[submissionModal] Fetching "${SUBMISSION_HTML_PATH}"...`);
      const resp = await fetch(SUBMISSION_HTML_PATH);
      if (!resp.ok) {
        console.error(`[submissionModal] Failed to load: ${resp.status} ${resp.statusText}`);
        throw new Error(`Failed to load submission.html (${resp.status})`);
      }
      const html = await resp.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const modal = doc.querySelector('#submission-modal');
      if (!modal) {
        console.error('[submissionModal] No #submission-modal found in loaded HTML!');
        throw new Error('No #submission-modal in submission.html');
      }
      document.getElementById('submission-modal-body').innerHTML = '';
      document.getElementById('submission-modal-body').appendChild(modal);
      submissionModalLoaded = true;
      console.log('[submissionModal] Modal HTML injected into #submission-modal-body');
    } else {
      console.log('[submissionModal] Modal already loaded, skipping fetch.');
    }

    setupSubmissionModalListeners();
    await populateSubmissionModalFields();
    showSubmissionModal();
  } catch (e) {
    console.error('[submissionModal] ERROR in loadSubmissionModal:', e);
    alert('Unable to open Submission modal: ' + (e.message || e));
  }
}

/**
 * Sets up all listeners, including Browse buttons and ESC close.
 */
function setupSubmissionModalListeners() {
  console.log('[submissionModal] Setting up modal listeners...');

  const modal = document.getElementById('submission-modal');
  if (!modal) {
    console.error('[submissionModal] Cannot wire listeners—modal not found!');
    return;
  }

  // --- Modal close by [X] ---
  const closeBtn = document.getElementById('close-submission-modal');
  if (closeBtn) {
    closeBtn.onclick = () => {
      modal.style.display = 'none';
      console.log('[submissionModal] Modal closed by [X] button.');
    };
    console.log('[submissionModal] Wired [X] close button.');
  } else {
    console.warn('[submissionModal] No close-submission-modal button found!');
  }

  // --- Submit Button ---
  const submitBtn = document.getElementById('btn-start-submission');
  if (submitBtn) {
    submitBtn.onclick = onSubmissionModalSubmit;
    console.log('[submissionModal] Wired submit button.');
  } else {
    console.warn('[submissionModal] No btn-start-submission button found!');
  }

  // --- Browse Template Button ---
  let browseTemplateBtn = document.getElementById('browse-template-filename');
  if (!browseTemplateBtn) {
    // Dynamically add the button if not present (for older HTML)
    const input = document.getElementById('template-filename');
    if (input && !document.getElementById('browse-template-filename')) {
      browseTemplateBtn = document.createElement('button');
      browseTemplateBtn.type = 'button';
      browseTemplateBtn.id = 'browse-template-filename';
      browseTemplateBtn.textContent = 'Browse…';
      input.parentNode.appendChild(browseTemplateBtn);
      console.log('[submissionModal] Added missing browse-template-filename button.');
    }
  }
  if (browseTemplateBtn) {
    browseTemplateBtn.onclick = async () => {
      console.log('[submissionModal] Browse… for template file clicked.');
      try {
        const file = await browseTemplateFile();
        if (file) {
          document.getElementById('template-filename').value = file;
          console.log('[submissionModal] Template path set to:', file);
        }
      } catch (err) {
        console.error('[submissionModal] Error during template file browse:', err);
      }
    };
    console.log('[submissionModal] Wired browse-template-filename button.');
  } else {
    console.warn('[submissionModal] No browse-template-filename button found!');
  }

  // --- Browse Output File Button ---
  let browseOutputBtn = document.getElementById('browse-output-path');
  if (!browseOutputBtn) {
    // Dynamically add the button if not present (for older HTML)
    const input = document.getElementById('output-path');
    if (input && !document.getElementById('browse-output-path')) {
      browseOutputBtn = document.createElement('button');
      browseOutputBtn.type = 'button';
      browseOutputBtn.id = 'browse-output-path';
      browseOutputBtn.textContent = 'Browse…';
      input.parentNode.appendChild(browseOutputBtn);
      console.log('[submissionModal] Added missing browse-output-path button.');
    }
  }
	if (browseOutputBtn) {
		browseOutputBtn.onclick = async () => {
			console.log('[submissionModal] Browse… for output file clicked.');
			try {
				const file = await browseSaveFile({
					title: "Select output file location",
					default_filename: "Quote.docx",
					filetypes: [["Word Document", "*.docx"]]
				});
				let path = null;
				if (Array.isArray(file) && file[0]) {
					path = file[0];
				} else if (typeof file === "string" && file) {
					path = file;
				}
				if (path) {
					// Ensure .docx extension (case-insensitive)
					if (!path.toLowerCase().endsWith('.docx')) {
						path += '.docx';
					}
					document.getElementById('output-path').value = path;
					console.log('[submissionModal] Output path set to:', path);
				}
			} catch (err) {
				console.error('[submissionModal] Error during output file browse:', err);
			}
		};
	}
	else {
	  console.warn('[submissionModal] No browse-output-path button found!');
	}


  // --- ESC closes modal ---
  document.removeEventListener('keydown', submissionModalEscListener);
  document.addEventListener('keydown', submissionModalEscListener);
  console.log('[submissionModal] ESC key handler wired.');
}

/**
 * Handles ESC key to close modal.
 */
function submissionModalEscListener(e) {
  const modal = document.getElementById('submission-modal');
  if (e.key === 'Escape' && modal && modal.style.display === 'block') {
    modal.style.display = 'none';
    console.log('[submissionModal] Modal closed by ESC key.');
  }
}

/**
 * Populates modal fields from the current app settings.
 */
async function populateSubmissionModalFields() {
  console.log('[submissionModal] Populating modal fields from settings...');
  try {
    const settings = await getAppSettings();
    document.getElementById('template-filename').value = settings.TEMPLATE_FILENAME || '';
    document.getElementById('output-path').value = settings.OUTPUT_PATH || '';
    console.log('[submissionModal] Fields set:', settings);
  } catch (err) {
    console.warn('[submissionModal] Could not fetch settings:', err);
    document.getElementById('template-filename').value = '';
    document.getElementById('output-path').value = '';
  }
  document.getElementById('submission-status').textContent = '';
  document.getElementById('submission-progress').value = 0;
}

/**
 * Shows the modal.
 */
function showSubmissionModal() {
  const modal = document.getElementById('submission-modal');
  if (modal) {
    modal.style.display = 'block';
    console.log('[submissionModal] Modal displayed.');
  } else {
    console.error('[submissionModal] Cannot show modal—modal not found!');
  }
}

/**
 * Handles the actual submission process.
 */
async function onSubmissionModalSubmit() {
  console.log('[submissionModal] Submission started.');
  const statusEl = document.getElementById('submission-status');
  const progressEl = document.getElementById('submission-progress');
  const templatePath = document.getElementById('template-filename').value.trim();
  const outputPath = document.getElementById('output-path').value.trim();

  statusEl.textContent = 'Generating document...';
  progressEl.value = 10;

  if (!templatePath || !outputPath) {
    statusEl.textContent = 'Missing template or output path!';
    progressEl.value = 0;
    console.warn('[submissionModal] Validation failed: Missing template or output path.');
    return;
  }

  try {
    statusEl.textContent = 'Submitting to backend...';
    progressEl.value = 30;
    console.log(`[submissionModal] Calling backend: templatePath="${templatePath}", outputPath="${outputPath}"`);
    await window.pywebview.api.submit_quote(templatePath, outputPath);

    statusEl.textContent = 'Submission complete!';
    progressEl.value = 100;
    console.log('[submissionModal] Submission completed successfully.');

    // Auto-close after delay
    setTimeout(() => {
      document.getElementById('submission-modal').style.display = 'none';
      console.log('[submissionModal] Modal auto-closed after success.');
    }, 1500);
  } catch (e) {
    statusEl.textContent = 'Submission failed: ' + (e.message || e);
    progressEl.value = 0;
    console.error('[submissionModal] Submission failed:', e);
  }
}

// Make status update available for pywebview
window.updateSubmissionStatus = function(msg) {
    const statusEl = document.getElementById('submission-status');
    if (statusEl) statusEl.textContent = msg;
};


