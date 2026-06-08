// Edits persist to content.js via serve.py (no localStorage / no cache reliance).
// Loading works on file:// and http://; saving requires `python3 serve.py`.

const PAGE = location.pathname.split('/').pop() || 'index.html';

function getEditables() {
  return document.querySelectorAll('.content-block h2, .content-block p, .content-block li:not(.post-item)');
}

function load() {
  const data = (window.CONTENT || {})[PAGE];
  if (!data) return;
  getEditables().forEach((el, i) => {
    if (data[i] !== undefined) el.innerHTML = data[i];
  });
}

async function save(btn) {
  const data = {};
  getEditables().forEach((el, i) => { data[i] = el.innerHTML; });

  if (window.CONTENT) window.CONTENT[PAGE] = data;

  try {
    const res = await fetch('/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page: PAGE, data })
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
  } catch (e) {
    if (btn) btn.textContent = 'save failed — run serve.py';
    console.error('Save failed:', e);
    return false;
  }
  return true;
}

function enableEdit() {
  getEditables().forEach(el => {
    el.contentEditable = 'true';
    el.spellcheck = false;
  });
  document.body.classList.add('edit-mode');
  document.getElementById('edit-toggle').textContent = 'done';
}

async function disableEdit(btn) {
  getEditables().forEach(el => { el.contentEditable = 'false'; });
  document.body.classList.remove('edit-mode');
  btn.textContent = 'saving…';
  const ok = await save(btn);
  if (ok) btn.textContent = 'edit';
}

document.addEventListener('DOMContentLoaded', () => {
  load();

  // Edit button only on local dev — never on deployed sites
  const isLocal = ['localhost', '127.0.0.1', ''].includes(location.hostname);
  if (!isLocal) return;

  const btn = document.createElement('button');
  btn.id = 'edit-toggle';
  btn.textContent = 'edit';
  document.querySelector('nav').appendChild(btn);

  let editing = false;
  btn.addEventListener('click', () => {
    editing = !editing;
    editing ? enableEdit() : disableEdit(btn);
  });
});
