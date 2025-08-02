// base.js

document.addEventListener('DOMContentLoaded', () => {
  // Helper: fetch kèm CSRF & credentials
  async function ajaxFetch(url, options = {}) {
    const tokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
    const headers = options.headers || {};
    if (tokenEl) {
      headers['X-CSRFToken'] = tokenEl.value;
    }
    const opts = {
      credentials: 'same-origin',
      ...options,
      headers
    };
    return fetch(url, opts);
  }

  // Xử lý chung cho click và submit
  async function handleRequest({ url, method, body, confirmMsg, redirectTo }) {
    if (confirmMsg && !confirm(confirmMsg)) return;
    console.log('[base.js] Request', method, url);
    try {
      const resp = await ajaxFetch(url, { method, body });
      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(text || resp.statusText);
      }
      if (redirectTo) {
        window.location.href = redirectTo;
      } else {
        window.location.reload();
      }
    } catch (err) {
      console.error(err);
      alert('Lỗi: ' + err.message);
    }
  }

  // A. Delegate click trên <a[data-method]> & <button[data-method]>
  document.body.addEventListener('click', e => {
    const el = e.target.closest('a[data-method], button[data-method]');
    if (!el) return;

    e.preventDefault();
    const url        = el.dataset.url || el.getAttribute('href');
    const method     = el.dataset.method.toUpperCase();
    const confirmMsg = el.dataset.confirm;
    handleRequest({ url, method, confirmMsg });
  });

  // B. Intercept submit trên <form[data-method]>
  document.querySelectorAll('form[data-method]').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();

      const url        = form.dataset.url || form.action;
      const method     = (form.dataset.method || form.method).toUpperCase();
      const confirmMsg = form.dataset.confirm;
      const redirectTo = form.dataset.redirect;
      const body       = new FormData(form);

      handleRequest({ url, method, body, confirmMsg, redirectTo });
    });
  });
});
