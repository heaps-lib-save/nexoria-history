(() => {
  'use strict';
  const events = [...document.querySelectorAll('.event')];
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const search = document.querySelector('#search');
  const status = document.querySelector('#result-status');
  let selected = '全部';
  document.querySelector('.tools').hidden = false;

  function filter() {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const event of events) {
      const match = (selected === '全部' || event.dataset.category === selected) && event.textContent.toLocaleLowerCase().includes(query);
      event.hidden = !match;
      if (match) count++;
    }
    for (const heading of document.querySelectorAll('.year-heading')) {
      const year = heading.id.replace('year-', '');
      heading.hidden = !events.some(event => event.dataset.year === year && !event.hidden);
    }
    status.textContent = selected === '全部' && !query ? `共 ${count} 条记录` : `找到 ${count} 条记录`;
    document.querySelector('.empty-state').hidden = count !== 0;
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === selected)));
  }
  buttons.forEach(button => button.addEventListener('click', () => { selected = button.dataset.filter; filter(); }));
  search.addEventListener('input', filter);
  document.querySelector('#reset-filters').addEventListener('click', () => { search.value = ''; selected = '全部'; filter(); search.focus(); });
  document.querySelectorAll('.year-nav a').forEach(link => link.addEventListener('click', () => { search.value = ''; selected = '全部'; filter(); }));

  const viewer = document.querySelector('#image-viewer');
  if (typeof viewer.showModal === 'function') {
    let lastLink;
    const image = document.querySelector('#full-image');
    document.querySelectorAll('.image-link').forEach(link => link.addEventListener('click', event => {
      event.preventDefault();
      lastLink = link;
      image.src = link.href;
      image.alt = link.dataset.caption;
      document.querySelector('#viewer-caption').textContent = link.dataset.caption;
      viewer.showModal();
      document.body.classList.add('viewer-open');
      document.querySelector('.viewer-image').scrollTop = 0;
    }));
    document.querySelector('#viewer-close').addEventListener('click', () => viewer.close());
    viewer.addEventListener('click', event => { if (event.target === viewer) { const rect = viewer.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) viewer.close(); } });
    viewer.addEventListener('close', () => { document.body.classList.remove('viewer-open'); lastLink?.focus(); image.removeAttribute('src'); });
  }
})();
