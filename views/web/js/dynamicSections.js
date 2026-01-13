// dynamicSections.js
// --------------------------------------------------
// Super-verbose dynamic slot injector & section adder
// --------------------------------------------------

import {
  getCategoryFields,
  getField,
  setField,
  clearField,
  getFileBrowseFields
} from './apiWrapper.js';
import { registerField } from './viewStore.js';
import {
  updateCostSheetTotal,
  updateProjectMilestones
} from './milestones.js';

// internalKey → human category mapping
const keyToCategory = {};

// File browse configuration loaded from Python
let fileBrowseFields = {};

function loadBrowseFields() {
  if (!window.pywebview?.api) {
    console.log('[dynamicSections] pywebview not ready – waiting');
    window.addEventListener('pywebviewready', loadBrowseFields);
    return;
  }
  getFileBrowseFields()
    .then(fields => {
      fileBrowseFields = fields;
      console.log('[dynamicSections] Loaded fileBrowseFields:', fileBrowseFields);
    })
    .catch(err => {
      console.error('[dynamicSections] Error loading fileBrowseFields', err);
    });
}
loadBrowseFields();
/**
 * Decide if a field should show a "Browse…" button
 */
function shouldShowBrowse(category, fieldPath) {
  const paths = fileBrowseFields[category] || [];
  return paths.some(base => fieldPath.includes(base));
}

/**
 * Register a categoryKey so addSection knows which human
 * category name corresponds to that key.
 */
export function registerAddButton(internalKey, humanCategory) {
  console.log(`[registerAddButton] mapping "${internalKey}" → category="${humanCategory}"`);
  keyToCategory[internalKey] = humanCategory;
}

/**
 * Creates a <div class="field-row"> for the given field definition.
 */
function createFieldRow(field) {
  const row = document.createElement('div');
  row.className = 'field-row';
  if (field.optional) row.classList.add('optional');
  if (/description/i.test(field.key) || /description/i.test(field.label)) {
    row.classList.add('description-row');
  }
  return row;
}

/**
 * Creates a <label> for the given field definition.
 */
function createLabel(field) {
  const labelEl = document.createElement('label');
  labelEl.htmlFor = field.key;
  labelEl.textContent = `${field.label}:`;
  return labelEl;
}

/**
 * Ensure dynamic slots exist for any repeated fields
 */
export async function ensureDynamicSlots(flatData) {
  console.log('\n🚀 [ensureDynamicSlots] Starting dynamic slot scan');
  const targetIndexByKey = {};
  Object.keys(flatData).forEach(fullKey => {
    console.log(`🔍 Scanning flatData key="${fullKey}"`);
    const m = fullKey.match(/^data\.([^.]+)\.[^.]+\.(\d+)$/);
    if (!m) return;
    const [ , internalKey, idxStr ] = m;
    const idx = parseInt(idxStr, 10);
    const prev = targetIndexByKey[internalKey] || 1;
    targetIndexByKey[internalKey] = Math.max(prev, idx);
  });

  for (const [internalKey, targetIdx] of Object.entries(targetIndexByKey)) {
    console.log(`\n⚙️  internalKey="${internalKey}": target highest index = ${targetIdx}`);
    const rendered = Array.from(document.querySelectorAll('[data-field-key]'))
      .filter(el => el.dataset.fieldKey.startsWith(`data.${internalKey}.`));
    let maxRendered = 1;
    rendered.forEach(el => {
      const m2 = el.dataset.fieldKey.match(/\.(\d+)$/);
      if (m2) maxRendered = Math.max(maxRendered, parseInt(m2[1], 10));
    });
    console.log(`   ↳ Current maxRenderedIndex = ${maxRendered}`);
    const toAdd = targetIdx - maxRendered;
    console.log(`   ↳ Rows missing = ${toAdd}`);
    if (toAdd > 0) {
      for (let i = 1; i <= toAdd; i++) {
        console.log(`      → addSection("${internalKey}") [${i}/${toAdd}]`);
        await addSection(internalKey);
      }
    }
  }
  console.log('✅ [ensureDynamicSlots] Done.\n');
}

/**
 * Adds exactly one new dynamic section for internalKey
 */
export async function addSection(internalKey) {
  console.log(`\n[addSection] Called for internalKey="${internalKey}"`);
  const category = keyToCategory[internalKey];
  console.log(`  ↳ Mapped to category="${category}"`);
  const containerId = `${category.replace(/\s+/g, '')}-container`;
  const container   = document.getElementById(containerId);
  console.log(`  ↳ Found container id="${containerId}" →`, container);
  let maxIndex = 0;
  const prefix     = `data.${internalKey}.`;
  const idEls = container.querySelectorAll(`[id^="${prefix}"]`);
  idEls.forEach(el => {
    const parts = el.id.split('.');
    const last = parts[parts.length-1];
    const num = parseInt(last, 10);
    if (!isNaN(num)) maxIndex = Math.max(maxIndex, num);
  });
  const newIndex = maxIndex + 1;
  console.log(`  ↳ Computed newIndex = ${newIndex}`);
  const sectionWrapper = document.createElement('div');
  sectionWrapper.className = 'dynamic-section';
  sectionWrapper.dataset.dynamicIndex = newIndex;
  console.log('  ↳ Created sectionWrapper');

  const canonical = await getCategoryFields(category);
  console.log(`  ↳ Retrieved ${canonical.length} field definitions`);

  for (const fieldDef of canonical) {
    const newKey = fieldDef.key.replace(/\.\d+$/, `.${newIndex}`);
    const baseLab = fieldDef.label.replace(/\s*\d+$/, '').trim();

    const rowDiv  = createFieldRow({ ...fieldDef, key: newKey });
    const labelEl = createLabel({ ...fieldDef, key: newKey, label: fieldDef.label });
    labelEl.htmlFor     = newKey;
    labelEl.textContent = `${baseLab} ${newIndex}:`;
    rowDiv.appendChild(labelEl);

    let inputEl;
    if (/description/i.test(fieldDef.key)) {
      inputEl = document.createElement('textarea');
      inputEl.id = inputEl.name = newKey;
      inputEl.dataset.fieldKey = newKey;
      inputEl.addEventListener('input', () => {
        setField(newKey, inputEl.value).catch(err => console.error(`Error setting field ${newKey}`, err));
      });
      console.log(`    ↳ Created textarea for "${newKey}"`);
    } else {
      inputEl = document.createElement('input');
      inputEl.type           = 'text';
      inputEl.id             = inputEl.name = newKey;
      inputEl.dataset.fieldKey = newKey;
      inputEl.addEventListener('input', () => {
        setField(newKey, inputEl.value).catch(err => console.error(`Error setting field ${newKey}`, err));
      });
      console.log(`    ↳ Created text input for "${newKey}"`);
    }
    registerField(newKey);
    rowDiv.appendChild(inputEl);

    // 🔍 Browse button for eligible file fields
    if (shouldShowBrowse(category, newKey)) {
      console.log(`[dynamicSections] Adding Browse for "${newKey}"`);
      const browseBtn = document.createElement('button');
      browseBtn.type      = 'button';
      browseBtn.className = 'browse-btn';
      browseBtn.textContent = 'Browse…';
      browseBtn.addEventListener('click', async () => {
        try {
          const path = await window.pywebview.api.browse_file_field();
          console.log(`[dynamicSections] browse returned for "${newKey}":`, path);
          if (inputEl.tagName === 'INPUT') inputEl.value = path;
          await setField(newKey, path);
        } catch (err) {
          console.error(`[dynamicSections] Error browsing file for "${newKey}"`, err);
        }
      });
      rowDiv.appendChild(browseBtn);
    }

    // cost-sheet handlers
    if (category.toLowerCase() === 'cost sheet' && !/total/i.test(newKey)) {
      inputEl.addEventListener('blur', () => {
        updateCostSheetTotal(newIndex);
        updateProjectMilestones(newIndex);
      });
      console.log(`    ↳ Wired cost-sheet handlers for "${newKey}"`);
    }

    sectionWrapper.appendChild(rowDiv);
    console.log(`    ↳ Appended rowDiv for "${newKey}"`);
  }

  const deleteBtn = document.createElement('button');
  deleteBtn.type      = 'button';
  deleteBtn.className = 'dynamic-button delete-button';
  deleteBtn.textContent = `Delete entry ${newIndex}`;
  deleteBtn.addEventListener('click', () => deleteSection(internalKey, newIndex));
  sectionWrapper.appendChild(deleteBtn);
  console.log('  ↳ Appended delete button');

  container.appendChild(sectionWrapper);
  console.log(`[addSection] Completed injection for index ${newIndex}\n`);
}

/**
 * Remove a dynamic section and re-index later ones
 */
export async function deleteSection(internalKey, indexToDelete) {
  console.log(`[deleteSection] key="${internalKey}", index=${indexToDelete}`);
  const category = keyToCategory[internalKey];
  const containerId = `${category.replace(/\s+/g, '')}-container`;
  const container   = document.getElementById(containerId);

  // Remove target
  const sections = Array.from(container.querySelectorAll('.dynamic-section'));
  const toRemove = sections.find(s => parseInt(s.dataset.dynamicIndex, 10) === indexToDelete);
  if (toRemove) {
    toRemove.remove();
    console.log(`  ↳ Removed section ${indexToDelete}`);
  }

  // Re-index remaining sections
  for (const section of sections) {
    const idx = parseInt(section.dataset.dynamicIndex, 10);
    if (idx > indexToDelete) {
      const newIdx = idx - 1;
      section.dataset.dynamicIndex = newIdx;
      console.log(`  ↳ Shifting ${idx} → ${newIdx}`);

      // Update IDs, names, labels, and fieldKey dataset
      section.querySelectorAll('input, label, textarea').forEach(el => {
        ['id','name','htmlFor','dataset.fieldKey'].forEach(prop => {
          if (el[prop]) el[prop] = el[prop].replace(`.${idx}`, `.${newIdx}`);
        });
        if (el.tagName === 'LABEL') {
          const base = el.textContent.replace(/\s*\d+:/, '').trim();
          el.textContent = `${base} ${newIdx}:`;
        }
      });

      // Update this section's Delete button
      const delBtn = section.querySelector('button.delete-button');
      if (delBtn) {
        delBtn.textContent = `Delete entry ${newIdx}`;
        delBtn.onclick     = () => deleteSection(internalKey, newIdx);
        console.log(`    ↳ Updated Delete button to ${newIdx}`);
      }
    }
  }
}
