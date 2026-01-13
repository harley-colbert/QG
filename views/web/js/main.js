// js/main.js

import {
  getFileBrowseFields,
  getCategories,
  getSpecialLists,
  getSpellCheckCategories,
  getCategoryFields,
  categoryCanAdd,
  getOptionalCategories,
  newQuote,
  openQuote,
  saveQuote,
  setAllFields,
  setField,
  getField,
  calcOee,
  getProjectCost,
  computeMilestones,
  getAppSettings,
  updateAppSettings,
  browseFileField,
  getAllianceContacts
} from './apiWrapper.js';

import { loadSubmissionModal } from './submissionModal.js';
import { activeFieldKeys, unregisterField, viewStore, unregisterQuill, applyViewStore, quillInstances, registerQuill, registerField } from './viewStore.js';
import { registerAddButton, ensureDynamicSlots, addSection } from './dynamicSections.js';
import { initQuill, rehydrateQuills } from './quillSetup.js';
import { renderOeeSection } from './oeeDashboard.js';
import { updateCostSheetTotal, updateProjectMilestones } from './milestones.js';
import { loadSettingsModal, populateSettingsForm } from './settingsModal.js';
import { loadContactsModal  } from './contactsModal.js';

let fileBrowseMapping = {};

/**
 * Snapshot every plain field + every Quill editor into viewStore[type].
 *
 * @param {string} type  e.g. "budgetary" or "final"
 */
function saveViewStore(type) {
  const snapshot = {};

  // A) Capture every named form control: <input>, <select>, <textarea>
  document
    .querySelectorAll('input[name], select[name], textarea[name]')
    .forEach(el => {
      const key = el.dataset.fieldKey || el.name;
      if (!key) return;
      snapshot[key] = el.value ?? '';
    });

  // B) Capture OEE stat-cards by their IDs
  document.querySelectorAll('.oee-card').forEach(card => {
    const key = card.id;                // e.g. 'data.oee.oee'
    const span = card.querySelector('.big');
    if (!span) return;
    let val = span.textContent.trim();
    if (val.endsWith('%')) val = val.slice(0, -1).trim();
    snapshot[key] = val;
  });

  // C) Capture all your Quill editors
  Object.entries(quillInstances).forEach(([fieldKey, quill]) => {
    if (!quill || !quill.root) return;
    snapshot[fieldKey] = quill.root.innerHTML;
  });

  viewStore[type] = snapshot;
}



/** Renders all categories (and fields) for the given quote type */
/**
 * Renders all category blocks and their fields for a given quote type.
 * This method is fully verbose: logs every fetch, loop iteration, and DOM operation.
 *
 * @param {string} type  Quote type key (e.g. "budgetary" or "final")
 */
async function renderCategories(type = 'budgetary') {
  console.log(`\n[renderCategories] Starting render for quoteType="${type}"`);
  
  // Unregister every field so the next saveViewStore is clean
  console.log('  ↳ Unregistering all previously-registered fields');
  activeFieldKeys.forEach(key => unregisterField(key));

  // 1) Clear out existing content
  const mainContent = document.getElementById('main-content');
  console.log('  ↳ Clearing innerHTML of #main-content');
  mainContent.innerHTML = '';

  // 2) Reset any existing Quill instances
  console.log('  ↳ Calling rehydrateQuills({}) to reset editors');
  rehydrateQuills({});

  // 3) Fetch supporting metadata
  console.log('  ↳ Fetching optional headers list...');
  const optionalHeaders = await getOptionalCategories();
  console.log(`      • optionalHeaders: [${optionalHeaders.join(', ')}]`);

  console.log('  ↳ Fetching category definitions for this type...');
  const categories = await getCategories(type);
  console.log(`      • categories: [${categories.join(', ')}]`);

  console.log('  ↳ Fetching special lists (incoterms, etc.)...');
  const specialLists = await getSpecialLists();
  console.log(`      • specialLists.incoterms length: ${specialLists.incoterms.length}`);

  console.log('  ↳ Fetching spellcheck categories...');
  const spellcheckCategories = await getSpellCheckCategories();
  console.log(`      • spellcheckCategories: [${spellcheckCategories.join(', ')}]`);

  // 4) Loop over each category block
  for (const category of categories) {
    console.log(`\n  [renderCategories] Processing category="${category}"`);

    const isOptional = optionalHeaders.includes(category);
    console.log(`    ↳ isOptional? ${isOptional}`);

    const groupDiv = createCategoryGroup(category, isOptional);
    const fieldsContainer = groupDiv.querySelector('.fields-container');

    // 4a) Special-case OEE Metrics: render via custom helper
    if (category === 'OEE Metrics') {
      console.log('    ↳ Category is "OEE Metrics" → calling renderOeeSection()');
      renderOeeSection(groupDiv);
      mainContent.appendChild(groupDiv);
      console.log('    ↳ Appended OEE Metrics section to #main-content');
      continue;
    }

    // 4b) Grab the canonical field definitions and stash for dynamic-add
    console.log(`    ↳ Fetching field definitions via getCategoryFields("${category}")`);
    const fieldDefinitions = await getCategoryFields(category);
    console.log(`      • Retrieved ${fieldDefinitions.length} field definitions`);
    const internalKey = fieldDefinitions[0]?.key.split('.')[1] || '';
    window.categoryFieldDefs = window.categoryFieldDefs || {};
    window.categoryFieldDefs[internalKey] = fieldDefinitions;
    console.log(`      • Stash window.categoryFieldDefs["${internalKey}"] = [ ... ]`);

    // 4c) If this category supports dynamic-add, register & place an Add button
    if (await categoryCanAdd(category) && fieldDefinitions.length) {
      console.log(`    ↳ categoryCanAdd("${category}") → true; registering Add`);
      registerAddButton(internalKey, category);
      const addBtn = createAddButton(internalKey);
      fieldsContainer.appendChild(addBtn);
      console.log('      • Appended Add button to fields-container');
    } else {
      console.log(`    ↳ categoryCanAdd("${category}") → false or no fields; skipping Add`);
    }

    // 4d) Build each static field row
    const browseFieldsForCategory = fileBrowseMapping[category] || [];
    console.log(`    ↳ fileBrowseMapping for category="${category}": [${browseFieldsForCategory.join(', ')}]`);

    for (const fieldDef of fieldDefinitions) {
      console.log(`      • Rendering field key="${fieldDef.key}", label="${fieldDef.label}"`);

      // i) Create row wrapper + label
      const rowDiv = createFieldRow(fieldDef);
      rowDiv.appendChild(createLabel(fieldDef));
      console.log('        ↳ Created rowDiv and appended its <label>');

      // ii) Create appropriate input (text/select/quill/etc.)
      console.log('        ↳ Creating input element via createFieldInput(...)');
      const inputElement = await createFieldInput({
        category,
        field: fieldDef,
        specialLists,
        spellcheckCats: spellcheckCategories
      });

      if (inputElement) {
        console.log('        ↳ Appending input element to rowDiv');
        rowDiv.appendChild(inputElement);

        console.log('        ↳ Wiring up change/browse/cost-sheet handlers');
        setupInputField(inputElement, fieldDef, category, browseFieldsForCategory, rowDiv);
      } else {
        console.warn('        ⚠️ createFieldInput returned null/undefined for key=', fieldDef.key);
      }

      // iii) Append this row into the container
      fieldsContainer.appendChild(rowDiv);
      console.log('        ↳ Appended rowDiv to fields-container');
    }

    // 4e) Attach the fully built group back into the page
    mainContent.appendChild(groupDiv);
    console.log(`    ↳ Appended category-group "${category}" to #main-content`);
  }

  // 5) Re-apply any stored values into the newly-rendered inputs
  console.log('\n[renderCategories] Calling applyViewStore for type="' + type + '"');
  applyViewStore(type);
  console.log('[renderCategories] Complete for quoteType="' + type + '"\n');
}


/**
 * Creates a category container with a header and an inner wrapper
 * where both static and dynamic field-rows will live.
 *
 * @param {string} category       Human-readable category name (e.g. "System Description")
 * @param {boolean} isOptional    Whether to mark this entire group as optional
 * @returns {HTMLDivElement}      The fully-wired category-group element
 */
function createCategoryGroup(category, isOptional = false) {
  console.log(`[createCategoryGroup] begin: category="${category}", isOptional=${isOptional}`);

  // 1) Create outer wrapper
  const groupDiv = document.createElement('div');
  groupDiv.className = 'category-group';
  groupDiv.dataset.category = category;  
  console.log(`  ↳ Created <div class="category-group"> with dataset.category="${category}"`);

  // 2) Mark optional if needed
  if (isOptional) {
    groupDiv.classList.add('optional');
    console.log(`  ↳ Added CSS class "optional" to category-group for "${category}"`);
  }

  // 3) Generate and assign a stable ID
  const sanitizedId = category.replace(/\s+/g, '');
  const containerId = `${sanitizedId}-container`;
  groupDiv.id = containerId;
  console.log(`  ↳ Assigned id="${containerId}"`);

  // 4) Build inner HTML structure: a header plus a fields-container
  groupDiv.innerHTML = `
    <h2>${category}</h2>
    <div class="fields-container"></div>
  `;
  console.log('  ↳ Populated innerHTML with <h2> and <div class="fields-container">');

  console.log(`[createCategoryGroup] end for category="${category}"\n`);
  return groupDiv;
}

function createFieldRow(field) {
  const r = document.createElement('div');
  r.className = 'field-row';
  if (field.optional) r.classList.add('optional');
  if (/description/i.test(field.key) || /description/i.test(field.label)) {
    r.classList.add('description-row');
  }
  return r;
}

function createLabel(field) {
  const l = document.createElement('label');
  l.htmlFor = field.key;
  l.textContent = `${field.label}:`;
  return l;
}

function getCurrentQuoteType() {
	return document.getElementById('quote-type-select').value;
}

async function createFieldInput({ category, field, specialLists, spellcheckCats }) {
  // 1️⃣ Milestones dropdown
  
  if (field.key.startsWith('data.projectMilestones.')) {
    console.log(`[createFieldInput] Rendering milestones dropdown for ${field.key}`);
    const sel = document.createElement('select');
    sel.id = sel.name = field.key;

    const opts = specialLists.weeks_after_po || [];
    sel.append(new Option('— select week —', ''));
    opts.forEach(opt => sel.add(new Option(opt, opt)));

    registerField(field.key);
	console.log(`[register ViewStore] registered key ${field.key}`);
    return sel;
  }

  // 2️⃣ Sales Contact dropdown
  if (/^sales contact$/i.test(field.label.trim())) {
    const select = document.createElement('select');
    select.id = select.name = field.key;
    const contacts = await getAllianceContacts();
    select.innerHTML = `
      <option value="">— select contact —</option>
      ${contacts.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
    `;
    const existingName = await getField(field.key);
    if (existingName) {
      const match = contacts.find(c => c.name === existingName);
      if (match) select.value = match.id;
    }
    select.addEventListener('change', async () => {
      const id = select.value;
      const contact = contacts.find(c => String(c.id) === id);
      if (!contact) return;
      const base = field.key.split('.').slice(0, -1).join('.');
      const map = { title: contact.title, cell: contact.phone, email: contact.email };
      for (const [suffix, val] of Object.entries(map)) {
        const full = `${base}.${suffix}`;
        const el = document.getElementsByName(full)[0];
        if (el) { el.value = val || ''; await setField(full, val || ''); }
      }
      await setField(field.key, contact.name);
	  saveViewStore(getCurrentQuoteType());
      console.log(`[register ViewStore] registered key ${field.key}`);
    });
    registerField(field.key);
	console.log(`[register ViewStore] registered key ${field.key}`);
    return select;
  }

  // 3️⃣ Rich-text (Quill)
  if (/description/i.test(field.key)) {
    const wrapper = document.createElement('div');
    wrapper.className = 'field-input';
    const hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.id = hidden.name = field.key;
    wrapper.appendChild(hidden);
    const editor = document.createElement('div');
    editor.className = 'quill-editor';
    editor.id = `editor-${field.key}`;
	console.log(`[register ViewStore] registered key ${field.key}`);
    wrapper.appendChild(editor);

    const quill = initQuill(field.key, editor);
    registerQuill(field.key, quill);
    return wrapper;
  }

  // 4️⃣ Shipping Information dropdown
  if (category === 'Shipping Information') {
    const sel = document.createElement('select');
    sel.id = sel.name = field.key;
    specialLists.incoterms.forEach(opt => sel.add(new Option(opt, opt)));
	console.log(`[register ViewStore] registered key ${field.key}`);
    registerField(field.key);
    return sel;
  }

  // 5️⃣ Default text input
  const inp = document.createElement('input');
  inp.type       = 'text';
  inp.id         = inp.name = field.key;
  inp.readOnly   = field.key.toLowerCase().includes('total');
  inp.spellcheck = spellcheckCats.includes(category);
  try {
    const val = await getField(field.key);
    if (val != null) inp.value = val;
  } catch {}
  registerField(field.key);
  console.log(`[register ViewStore] registered key ${field.key}`);
  return inp;
}

function setupInputField(inputEl, field, category, browseFields, row) {
  // 1️⃣ Wire up change handler
  if (!inputEl.readOnly) {
    inputEl.addEventListener('input', () =>
      setField(field.key, inputEl.value)
        .catch(() => console.error('Error setting field', field.key))
    );
	saveViewStore(getCurrentQuoteType());
	console.log(`[register ViewStore] registered key ${field.key}`);
  }

  // 2️⃣ Debug what we're comparing
  console.log('[Browse] Available paths:', browseFields);
  console.log('[Browse] Current field key:', field.key);

  // 3️⃣ “Contains” match instead of exact includes
  const shouldBrowse = browseFields.some(base => field.key.includes(base));
  if (shouldBrowse) {
    console.log(`[Browse] ✓ "${field.key}" matches one of ${browseFields}`);
    row.appendChild(createBrowseButton(inputEl, field));
  } else {
    console.log(`[Browse] ✗ "${field.key}" does not match any of ${browseFields}`);
  

  
}


/**
 * Returns a “Browse…” button wired to open the file dialog,
 * set the field, and then trigger cost‐sheet & milestone updates.
 */
function createBrowseButton(inputEl, field) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.textContent = 'Browse…';
  btn.addEventListener('click', async () => {
    try {
      // 1) Let the user pick a file
      const path = await window.pywebview.api.browse_file_field();
      console.log(`[Browse] Selected path for ${field.key}:`, path);
      if (!path) return;

      // 2) Update the input and backing field
      inputEl.value = path;
      await setField(field.key, path);
	  saveViewStore(getCurrentQuoteType());
	  console.log(`[register ViewStore] registered key ${field.key}`);	
      // 3) Immediately trigger Cost Sheet & Milestones
      if (field.key.includes('data.costSheet.link')) {
        const idx = field.key.split('.').pop();
        console.log(`[CostSheet] After browse: updating totals for index=${idx}`);
        updateCostSheetTotal(idx);
        updateProjectMilestones(idx);
      }
    } catch (err) {
      console.error(`[Browse] Error in browse for ${field.key}:`, err);
    }
  });
  return btn;
}

}

function createAddButton(key) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.classList.add('add-button', 'dynamic-button');
  btn.textContent = 'Add';
  btn.dataset.addCategory = key;
  btn.addEventListener('click', () => addSection(key));
  return btn;
}

function flattenData(obj, prefix = 'data') {
  return Object.entries(obj).reduce((acc, [k, v]) => {
    const p = prefix ? `${prefix}.${k}` : k;
    if (v != null && typeof v === 'object' && !Array.isArray(v)) {
      Object.assign(acc, flattenData(v, p));
    } else {
      acc[p] = v;
    }
    return acc;
  }, {});
}

/** Load a quote record into the form */
async function loadQuoteToForm({ quoteType, quotes }) {
  console.log('🚀 [loadQuoteToForm] Start loading quote of type:', quoteType);
  console.log('   ↳ Incoming flat data keys:', Object.keys(quotes));

  const sel = document.getElementById('quote-type-select');

  // 1) If the user switched quoteType, re-render everything (and rebuild Add buttons)
  if (sel.value !== quoteType) {
    console.log(`   ↳ Changing selector from "${sel.value}" → "${quoteType}"`);
    sel.value = quoteType;

    console.log('   ↳ Rendering categories for new quoteType');
    await renderCategories(quoteType);
    console.log('   ↳ Categories rendered');
  }

  

  // 3) Single dynamic slot pass (this is where the Add button is automatically clicked as needed)
  console.log('   ↳ 🔄 Ensuring dynamic slots (once)');
  await ensureDynamicSlots(quotes);

  // 4) Two pure-apply passes to bind values into any newly created fields
  console.log('   ↳ 🔄 Applying values – pass 1');
  innerApply(quotes);

  console.log('✅ [loadQuoteToForm] Finished loading quote');
}



function innerApply(data) {
  console.log('🔄 [innerApply] Starting value bind');
  console.log('   ↳ Incoming data keys:', Object.keys(data));

  Object.entries(data).forEach(([k, v]) => {
    console.log(`\n→ Processing key "${k}" with value:`, v);

    // 1) Skip rich-text (we handle via rehydrateQuills)
    if (k.includes('description')) {
      console.log(`   ↳ Skipping description key "${k}"`);
      return; 
    }

    // 2) Find the element by id
    const el = document.getElementById(k);
    if (!el) {
      console.warn(`   ⚠️  No element found with id="${k}", skipping`);
      return;
    }
    console.log(`   ↳ Found element <${el.tagName.toLowerCase()}>#${k}`);

    // 3) Apply the value
    if (el.tagName === 'SELECT') {
      // match option by value
      const optionIndex = [...el.options].findIndex(o => o.value === v);
      let chosen = optionIndex >= 0 ? optionIndex : 0;
	  chosen = chosen+1
      console.log(`     ↳ Setting <select> selectedIndex=${chosen} (value="${v}")`);
      el.selectedIndex = chosen;
    } else {
      console.log(`     ↳ Setting value of <${el.tagName.toLowerCase()}> to "${v}"`);
      el.value = v;
    }
  });

  // 4) Finally, rehydrate all your Quill editors
  console.log('\n🔄 Rehydrating Quill editors with data for descriptions');
  rehydrateQuills(data);

  console.log('✅ [innerApply] Complete');
}


async function init() {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init); return;
  }
  if (!window.pywebview?.api) {
    window.addEventListener('pywebviewready', init); return;
  }

  fileBrowseMapping = await getFileBrowseFields();

  const quoteSelect = document.getElementById('quote-type-select');
  await renderCategories(quoteSelect.value);

  quoteSelect._last = quoteSelect.value;
  quoteSelect.addEventListener('change', async () => {
    saveViewStore(quoteSelect._last);
    await renderCategories(quoteSelect.value);
    applyViewStore(quoteSelect.value);
    quoteSelect._last = quoteSelect.value;
  });

  document.getElementById('btn-savedoc').addEventListener('click', async () => {
    const type = document.getElementById('quote-type-select').value;
    saveViewStore(type);
    await setAllFields(viewStore[type]);
    try { await saveQuote(type); alert('Quote saved'); } catch { alert('Save failed'); }
  });

  document.getElementById('btn-new').addEventListener('click', async () => {
    await newQuote();
    document.querySelectorAll('.field-row input, .field-row select')
      .forEach(el => { el.tagName === 'SELECT' ? el.selectedIndex = 0 : el.value = ''; });
    rehydrateQuills({});
  });

  document.getElementById('btn-open').addEventListener('click', async () => {
    const payload = await openQuote();
    const record = Array.isArray(payload.quotes)
      ? payload.quotes[0]
      : Object.values(payload.quotes)[0];
    const flat = flattenData(record.data || {});
    await loadQuoteToForm({ quoteType: payload.quoteType, quotes: flat });
    viewStore[payload.quoteType] = payload.fields;
    applyViewStore(payload.quoteType);
  });

	// NEW: Handle modal submission to generate the Word doc
	document.getElementById('btn-submit').addEventListener('click', async () => {
    await loadSubmissionModal();
  });


  document.getElementById('btn-contacts').addEventListener('click', async () => {
	  await loadContactsModal (); // This will take care of dynamic injection and showing the modal
	});
		

  document.getElementById('btn-settings').addEventListener('click', async () => {
    await loadSettingsModal();
    const settings = await getAppSettings();
    populateSettingsForm(settings);
    document.getElementById('settings-modal').style.display = 'block';
  });
}

window.createFieldRow     = createFieldRow;
window.createLabel        = createLabel;
window.createFieldInput   = createFieldInput;
window.setupInputField    = setupInputField;

init();
