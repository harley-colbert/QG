// oeeDashboard.js

/**
 * Build one labelled numeric field for the left-hand form
 * @param {string} label – the visible label
 * @param {string} name  – the input’s id attribute
 * @returns {string} HTML string for a form row
 */
 import { registerField } from './viewStore.js';

 
function buildInputRow(label, name) {
  console.log(`[OEE] buildInputRow: ${label} → id="${name}"`);
  // `name` is the fieldKey (e.g., "data.oee.runtime")
  return `
    <div class="oee-row">
      <label>${label}</label>
      <input type="number" step="any"
             id="${name}"
             name="${name}"
             data-field-key="${name}" />
    </div>`;
}


/**
 * Build a single “stat card” for the right-hand results grid
 */
function card(title, key, green = false) {
  console.log(`[OEE] card: ${title} → key="${key}"`);
  const color = green ? 'green' : 'gray';
  return `
    <div class="oee-card ${color}" id="${key}">
      <span class="big"></span><span class="label">${title}</span>
    </div>`;
}

function debounce(fn, ms) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      console.log('[OEE] debounce → firing');
      fn.apply(this, args);
    }, ms);
  };
}

export function renderOeeSection(container) {
  console.log('[OEE] renderOeeSection:start');

  let lastRuntime = 0;

  // 1. Inject markup
  const markup = `
    <div class="oee-container">
      <div class="oee-form">
        ${buildInputRow('Runtime (hrs)',      'data.oee.runtime')}
        ${buildInputRow('Planned Downtime',   'data.oee.planneddowntime')}
        ${buildInputRow('Unplanned Downtime', 'data.oee.unplanneddowntime')}
        ${buildInputRow('Total Parts',        'data.oee.totalproduced')}
        ${buildInputRow('Cycle Time (sec)',   'data.oee.nominalcycletime')}
        ${buildInputRow('Total Scrap',        'data.oee.totalscrap')}
      </div>
      <div class="oee-cards">
        ${card('OEE',            'data.oee.oee',           true)}
        ${card('Capacity',       'data.oee.capacity')}
        ${card('Total Produced', 'data.oee.total_produced')}
        ${card('Performance',    'data.oee.performance',   true)}
        ${card('Quality',        'data.oee.quality',       true)}
        ${card('Availability',   'data.oee.availability',  true)}
      </div>
    </div>`;
  container.insertAdjacentHTML('beforeend', markup);
  console.log('[OEE] renderOeeSection:markup inserted');

  // 2. Attach listeners
  (function attach() {
	  const inputs = container.querySelectorAll('.oee-form input');
	  if (!inputs.length) {
		console.warn('[OEE] attach: no inputs yet, retrying');
		return setTimeout(attach, 50);
	  }
	  console.log(`[OEE] attach: found ${inputs.length} inputs`);
	  inputs.forEach(i => {
		console.log(`[OEE] attach: binding #${i.id}`);
		// Register for viewStore snapshots
		registerField(i.getAttribute('data-field-key') || i.name || i.id);
		i.addEventListener('input', debounce(runOeeCalc, 50));
	  });
	})();


  // 3. Build clean payload and call Python
  async function runOeeCalc() {
    console.log('[OEE] runOeeCalc:start');

    // read raw values by ID
    const raw = {};
    [
      'data.oee.runtime',
      'data.oee.planneddowntime',
      'data.oee.unplanneddowntime',
      'data.oee.totalproduced',
      'data.oee.nominalcycletime',
      'data.oee.totalscrap'
    ].forEach(id => {
      const el = container.querySelector(`[id="${id}"]`);
      raw[id] = el ? el.value : '';
    });
    console.log('[OEE] runOeeCalc:raw inputs', raw);

    // remap to Python names
    const payload = {
      runtime:           parseFloat(raw['data.oee.runtime'])       || 0,
      planned_downtime:  parseFloat(raw['data.oee.planneddowntime'])   || 0,
      unplanned_downtime:parseFloat(raw['data.oee.unplanneddowntime']) || 0,
      total_parts:       parseFloat(raw['data.oee.totalproduced'])     || 0,
      cycle_time:        parseFloat(raw['data.oee.nominalcycletime'])  || 0,
      total_scrap:       parseFloat(raw['data.oee.totalscrap'])        || 0
    };
    console.log('[OEE] runOeeCalc:payload →', payload);

    lastRuntime = payload.runtime;

    let result = {};
    try {
      console.log('[OEE] calling pywebview.api.calc_oee');
      result = await window.pywebview.api.calc_oee(payload);
      console.log('[OEE] got result →', result);
    } catch (e) {
      console.error('[OEE] calc_oee error', e);
      return;
    }
    updateCards(result);
  }

  // 4. Paint cards (including Capacity = parts/hr × runtime)
  function updateCards(data) {
    console.log('[OEE] updateCards:start', data);
    Object.entries(data).forEach(([key, val]) => {
      console.log(`[OEE] updateCards:key=${key}, val=${val}`);
      const span = container.querySelector(`.oee-card[id="data.oee.${key}"] .big`);
      if (!span) return console.warn(`[OEE] no span for ${key}`);

      let disp = val;
      if (key === 'capacity') {
        disp = (val * lastRuntime);
        console.log(`[OEE] capacity calc: ${val}×${lastRuntime}=${disp}`);
      }

      const pct = ['oee','performance','quality','availability'];
      span.textContent = pct.includes(key) ? `${disp} %` : disp;
      console.log(`[OEE] span#${key} → "${span.textContent}"`);

      if (key==='oee') {
        const warn = parseFloat(disp) < 85;
        span.closest('.oee-card').classList.toggle('warn', warn);
        console.log(`[OEE] warn=${warn}`);
      }
    });
    console.log('[OEE] updateCards:complete');
  }
}
