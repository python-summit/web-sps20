(() => {
  const dialog = document.querySelector('.photo-lightbox');
  const photoLinks = Array.from(document.querySelectorAll('.photo-link'));

  if (!dialog || !photoLinks.length || typeof dialog.showModal !== 'function') {
    return;
  }

  const image = dialog.querySelector('.photo-lightbox-media img');
  const media = dialog.querySelector('.photo-lightbox-media');
  const figure = dialog.querySelector('figure');
  const dayLabel = dialog.querySelector('.photo-lightbox-day');
  const counter = dialog.querySelector('.photo-lightbox-counter');
  const description = dialog.querySelector('.photo-lightbox-description');
  const sourceLink = dialog.querySelector('.photo-lightbox-source');
  const progress = dialog.querySelector('.photo-lightbox-progress span');
  const closeButton = dialog.querySelector('.photo-lightbox-close');
  const previousButton = dialog.querySelector('.photo-lightbox-previous');
  const nextButton = dialog.querySelector('.photo-lightbox-next');

  let galleryLinks = [];
  let currentIndex = 0;
  let opener = null;
  let pointerStart = null;

  function preload(index) {
    if (!galleryLinks.length) {
      return;
    }

    const link = galleryLinks[(index + galleryLinks.length) % galleryLinks.length];
    const preloadImage = new Image();
    preloadImage.src = link.href;
  }

  function show(index) {
    currentIndex = (index + galleryLinks.length) % galleryLinks.length;
    const link = galleryLinks[currentIndex];
    const position = Number(link.dataset.index);
    const total = Number(link.dataset.total);

    media.classList.add('loading');
    image.src = link.href;
    image.alt = link.dataset.alt || '';
    dayLabel.textContent = link.dataset.day || '';
    counter.textContent = `${position} / ${total}`;
    description.textContent = link.dataset.alt || '';
    sourceLink.href = link.href;
    progress.style.width = `${(position / total) * 100}%`;

    preload(currentIndex - 1);
    preload(currentIndex + 1);
  }

  function open(link) {
    galleryLinks = Array.from(
      link.closest('.photo-grid').querySelectorAll('.photo-link')
    );
    currentIndex = galleryLinks.indexOf(link);
    opener = link;
    show(currentIndex);
    dialog.showModal();
    document.body.classList.add('photo-viewer-open');
    closeButton.focus();
  }

  image.addEventListener('load', () => media.classList.remove('loading'));

  photoLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      open(link);
    });
  });

  closeButton.addEventListener('click', () => dialog.close());
  previousButton.addEventListener('click', () => show(currentIndex - 1));
  nextButton.addEventListener('click', () => show(currentIndex + 1));

  dialog.addEventListener('click', (event) => {
    if (event.target === dialog || event.target === figure) {
      dialog.close();
    }
  });

  dialog.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      show(currentIndex - 1);
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      show(currentIndex + 1);
    }
  });

  dialog.addEventListener('pointerdown', (event) => {
    pointerStart = { x: event.clientX, y: event.clientY };
  });

  dialog.addEventListener('pointerup', (event) => {
    if (!pointerStart) {
      return;
    }

    const distanceX = event.clientX - pointerStart.x;
    const distanceY = event.clientY - pointerStart.y;
    pointerStart = null;

    if (Math.abs(distanceX) < 60 || Math.abs(distanceX) < Math.abs(distanceY)) {
      return;
    }

    show(distanceX > 0 ? currentIndex - 1 : currentIndex + 1);
  });

  dialog.addEventListener('close', () => {
    document.body.classList.remove('photo-viewer-open');
    media.classList.remove('loading');
    image.removeAttribute('src');
    image.alt = '';
    sourceLink.href = '#';
    if (opener) {
      opener.focus();
    }
  });

  const dayLinks = Array.from(document.querySelectorAll('[data-day-link]'));
  const daySections = Array.from(document.querySelectorAll('[data-day-section]'));

  if ('IntersectionObserver' in window && daySections.length) {
    const dayObserver = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (!visible) {
          return;
        }

        dayLinks.forEach((link) => {
          const active = link.dataset.dayLink === visible.target.dataset.daySection;
          link.classList.toggle('active', active);
          if (active) {
            link.setAttribute('aria-current', 'true');
          } else {
            link.removeAttribute('aria-current');
          }
        });
      },
      { rootMargin: '-20% 0px -65% 0px', threshold: [0, 0.1] }
    );

    daySections.forEach((section) => dayObserver.observe(section));
  }
})();
