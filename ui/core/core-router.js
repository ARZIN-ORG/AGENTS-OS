import { viewRegistry } from './view-registry.js';

const mainEl = document.getElementById('main-content');

function loadView(viewKey) {
  const v = viewRegistry[viewKey];
  if (!v) {
    mainEl.innerHTML = '<div class="error">ویو پیدا نشد</div>';
    return;
  }

  fetch(v.html)
    .then(r => r.text())
    .then(html => {
      mainEl.innerHTML = html;
      if (v.js) {
        import(v.js).then(m => m.init && m.init()).catch(e => console.warn('JS init skipped:', e));
      }
    })
    .catch(() => mainEl.innerHTML = '<div class="error">خطا در بارگذاری ویو</div>');
}

export function navigateTo(hash) {
  const key = hash.replace('#/', '').split('?')[0];
  const cleanKey = key || 'overview';
  loadView(cleanKey);

  document.querySelectorAll('[data-nav]').forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === hash);
  });
}

window.addEventListener('hashchange', () => navigateTo(location.hash));
document.addEventListener('DOMContentLoaded', () => navigateTo(location.hash || '#/overview'));
