(() => {
  const root = document.documentElement;
  const themeButton = document.querySelector('[data-theme-toggle]');
  const savedTheme = localStorage.getItem('news-theme');
  root.dataset.theme = savedTheme === 'dark' ? 'dark' : 'light';

  themeButton?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('news-theme', root.dataset.theme);
  });

  const menuButton = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('#primary-nav');
  menuButton?.addEventListener('click', () => {
    const open = menu?.classList.toggle('is-open') || false;
    menuButton.setAttribute('aria-expanded', String(open));
  });

  const searchButton = document.querySelector('[data-search-toggle]');
  const searchForm = document.querySelector('[data-search-form]');
  searchButton?.addEventListener('click', () => {
    const opening = searchForm.hasAttribute('hidden');
    searchForm.toggleAttribute('hidden');
    searchButton.setAttribute('aria-expanded', String(opening));
    if (opening) searchForm.querySelector('input')?.focus();
  });

  document.querySelector('[data-share]')?.addEventListener('click', async () => {
    if (navigator.share) await navigator.share({title: document.title, url: location.href});
    else await navigator.clipboard.writeText(location.href);
  });

  const input = document.querySelector('[data-file-input]');
  const label = document.querySelector('[data-file-label]');
  const uploadButton = document.querySelector('[data-upload-button]');
  input?.addEventListener('change', () => {
    const file = input.files?.[0];
    if (file) {
      label.textContent = file.name;
      uploadButton.disabled = false;
    }
  });
  document.querySelector('[data-upload-form]')?.addEventListener('submit', () => {
    uploadButton.disabled = true;
    uploadButton.innerHTML = 'Uploading securely…';
  });

  const activeImports = [...document.querySelectorAll('[data-import-id]')].filter((row) => ['queued','processing'].includes(row.dataset.status));
  const poll = async (row) => {
    try {
      const response = await fetch(`/admin/imports/${row.dataset.importId}`, {headers: {'Accept': 'application/json'}});
      if (!response.ok) return;
      const job = await response.json();
      row.querySelector('[data-progress-bar]').style.width = `${job.progress}%`;
      row.querySelector('[data-progress-text]').textContent = `${job.progress}%`;
      row.querySelector('[data-stage]').textContent = job.stage;
      const status = row.querySelector('[data-status-label]');
      status.textContent = job.status;
      status.className = `status status-${job.status}`;
      if (['queued','processing'].includes(job.status)) setTimeout(() => poll(row), 2000);
      else location.reload();
    } catch (_) { setTimeout(() => poll(row), 5000); }
  };
  activeImports.forEach(poll);
})();
