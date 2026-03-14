const PAGE_KEY = 'v2:page:' + location.pathname;

function getEditables() {
  return document.querySelectorAll('main h1, main p, footer p');
}

function save() {
  const data = {};
  getEditables().forEach((el, i) => {
    data[i] = el.innerHTML;
  });
  localStorage.setItem(PAGE_KEY, JSON.stringify(data));
}

function load() {
  const raw = localStorage.getItem(PAGE_KEY);
  if (!raw) return;
  const data = JSON.parse(raw);
  getEditables().forEach((el, i) => {
    if (data[i] !== undefined) el.innerHTML = data[i];
  });
}

function enableEdit() {
  getEditables().forEach(el => {
    el.contentEditable = 'true';
    el.spellcheck = false;
  });
  document.body.classList.add('edit-mode');
  document.getElementById('edit-toggle').textContent = 'done';
}

function disableEdit() {
  getEditables().forEach(el => {
    el.contentEditable = 'false';
  });
  document.body.classList.remove('edit-mode');
  document.getElementById('edit-toggle').textContent = 'edit';
  save();
}

document.addEventListener('DOMContentLoaded', () => {
  load();

  const btn = document.createElement('button');
  btn.id = 'edit-toggle';
  btn.textContent = 'edit';
  document.querySelector('nav').appendChild(btn);

  let editing = false;
  btn.addEventListener('click', () => {
    editing = !editing;
    editing ? enableEdit() : disableEdit();
  });

  document.addEventListener('input', () => {
    if (editing) save();
  });
});
