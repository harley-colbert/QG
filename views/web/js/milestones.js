// milestones.js

import { getProjectCost, computeMilestones, getSpecialLists } from './apiWrapper.js';

/**
 * Update the “total” field for a given Cost Sheet index by fetching
 * the cost from Python and writing it into the corresponding input.
 *
 * @param {number|string} index – the dynamic section index
 */
export async function updateCostSheetTotal(index) {
  const linkFieldName  = `data.costSheet.link.${index}`;
  const totalFieldName = `data.costSheet.total.${index}`;
  const fileInput      = document.getElementsByName(linkFieldName)[0];
  const totalInput     = document.getElementsByName(totalFieldName)[0];

  if (fileInput && fileInput.value) {
    try {
      const total = await getProjectCost(fileInput.value);
      if (totalInput) {
        totalInput.value    = total;
        totalInput.readOnly = true;
      }
    } catch (err) {
      console.error(`Error updating cost sheet total for index ${index}:`, err);
    }
  }
}

/**
 * For a given Cost Sheet index, fetch milestone data from Python
 * and write each returned value into the corresponding form field.
 *
 * @param {number|string} index – the dynamic section index
 */
export async function updateProjectMilestones(index) {
  console.log(`updateProjectMilestones(${index})`);
  const linkFieldName = `data.costSheet.link.${index}`;
  const fileInput     = document.getElementsByName(linkFieldName)[0];

  if (!fileInput || !fileInput.value) {
    console.warn(`No file path provided for ${linkFieldName}`);
    return;
  }

  try {
    // 1) Fetch numeric week offsets (e.g. { customer_kickoff: 1, design_acceptance: 4, … })
    const raw = await computeMilestones(fileInput.value);
    console.log('← Milestones payload:', raw);

    // 2) Get the labels list ("Week 0 after PO", …)
    const { weeks_after_po: opts = [] } = await getSpecialLists();

    // 3) For each milestone, set the <select> to the correct label
    Object.entries(raw).forEach(([snakeKey, weekNumber]) => {
      // snake_case → camelCase
      const camel = snakeKey
        .split('_')
        .map((w,i) => i === 0 ? w : w[0].toUpperCase() + w.slice(1))
        .join('');
      const fullKey = `data.projectMilestones.${camel}`;

      // Find the <select> by name or id
      const el = document.getElementsByName(fullKey)[0] || document.getElementById(fullKey);
      if (!el) {
        console.warn(`✖ No element found for '${fullKey}'`);
        return;
      }
      if (el.tagName !== 'SELECT') {
        console.warn(`✖ Element for '${fullKey}' is not a <select>`);
        return;
      }

      // Determine the label to select (clamp into range)
      const label = opts[weekNumber] || opts[0] || '';
      console.log(` ► Setting <select>#${fullKey} value → "${label}"`);

      // 4) Set the select by value
      el.value = label;
    });
  } catch (err) {
    console.error(`Error updating project milestones for index ${index}:`, err);
  }
}
