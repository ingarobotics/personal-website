// === Apply saved colors immediately (avoid flash of default theme) ===
(function () {
  try {
    const saved = JSON.parse(localStorage.getItem('site:colors') || '{}');
    const r = document.documentElement;
    const bg   = saved.swap ? saved.text : saved.bg;
    const text = saved.swap ? saved.bg   : saved.text;
    if (bg)         r.style.setProperty('--bg-color',   bg);
    if (text)       r.style.setProperty('--text-color', text);
    if (saved.link) r.style.setProperty('--link-color', saved.link);
  } catch (e) { /* ignore */ }
})();

// === Build the floating color panel ===
const COLOR_KEY = 'site:colors';
const DEFAULTS  = { bg: '#2f5270', text: '#f0cd9a', link: '#cc8b5b', swap: false };
const HEX_RE    = /^#[0-9a-fA-F]{6}$/;

function getColors() {
  return Object.assign({}, DEFAULTS, JSON.parse(localStorage.getItem(COLOR_KEY) || '{}'));
}

function applyColors(c) {
  const r = document.documentElement;
  r.style.setProperty('--bg-color',   c.swap ? c.text : c.bg);
  r.style.setProperty('--text-color', c.swap ? c.bg   : c.text);
  r.style.setProperty('--link-color', c.link);
}

function saveAndApply(c) {
  localStorage.setItem(COLOR_KEY, JSON.stringify(c));
  applyColors(c);
}

function row(key, value) {
  return `
    <label>
      <span class="key-label">${key}</span>
      <input type="color" data-key="${key}" data-role="picker" value="${value}">
      <input type="text"  data-key="${key}" data-role="hex" value="${value}" maxlength="7" spellcheck="false">
    </label>
  `;
}

document.addEventListener('DOMContentLoaded', () => {
  const c = getColors();

  const panel = document.createElement('div');
  panel.id = 'color-panel';
  panel.innerHTML = `
    <button id="color-toggle" type="button" title="theme">◐</button>
    <div id="color-controls" hidden>
      ${row('bg',   c.bg)}
      ${row('text', c.text)}
      ${row('link', c.link)}
      <label class="swap-row"><input type="checkbox" id="swap-toggle" ${c.swap ? 'checked' : ''}> swap bg/text</label>
      <button id="reset-colors" type="button">reset</button>
    </div>
  `;
  document.body.appendChild(panel);

  document.getElementById('color-toggle').addEventListener('click', () => {
    document.getElementById('color-controls').toggleAttribute('hidden');
  });

  // Color picker → update hex input + apply
  panel.querySelectorAll('input[data-role="picker"]').forEach(picker => {
    picker.addEventListener('input', () => {
      const key = picker.dataset.key;
      const val = picker.value;
      panel.querySelector(`input[data-role="hex"][data-key="${key}"]`).value = val;
      const colors = getColors();
      colors[key] = val;
      saveAndApply(colors);
    });
  });

  // Hex input → update picker + apply (only when valid)
  panel.querySelectorAll('input[data-role="hex"]').forEach(hex => {
    hex.addEventListener('input', () => {
      const val = hex.value.trim();
      if (!HEX_RE.test(val)) return;
      const key = hex.dataset.key;
      panel.querySelector(`input[data-role="picker"][data-key="${key}"]`).value = val;
      const colors = getColors();
      colors[key] = val;
      saveAndApply(colors);
    });
  });

  document.getElementById('swap-toggle').addEventListener('change', (e) => {
    const colors = getColors();
    colors.swap = e.target.checked;
    saveAndApply(colors);
  });

  document.getElementById('reset-colors').addEventListener('click', () => {
    localStorage.removeItem(COLOR_KEY);
    location.reload();
  });
});
