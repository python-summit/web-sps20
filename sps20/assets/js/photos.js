(() => {
  const dialog = document.querySelector('.photo-lightbox');
  if (!dialog || typeof dialog.showModal !== 'function') {
    return;
  }

  const image = dialog.querySelector('img');
  const figure = dialog.querySelector('figure');
  const caption = dialog.querySelector('figcaption');
  const closeButton = dialog.querySelector('.photo-lightbox-close');
  const previousButton = dialog.querySelector('.photo-lightbox-previous');
  const nextButton = dialog.querySelector('.photo-lightbox-next');

  let links = [];
  let currentIndex = 0;
  let opener = null;
  let pointerStartX = null;

  function show(index) {
    currentIndex = (index + links.length) % links.length;
    const link = links[currentIndex];

    image.src = link.href;
    image.alt = link.dataset.alt || '';
    caption.textContent = `${link.dataset.index} / ${link.dataset.total}`;
  }

  function open(link) {
    links = Array.from(link.closest('.photo-grid').querySelectorAll('.photo-link'));
    currentIndex = links.indexOf(link);
    opener = link;
    show(currentIndex);
    dialog.showModal();
    closeButton.focus();
  }

  document.querySelectorAll('.photo-link').forEach((link) => {
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
    pointerStartX = event.clientX;
  });

  dialog.addEventListener('pointerup', (event) => {
    if (pointerStartX === null) {
      return;
    }

    const distance = event.clientX - pointerStartX;
    pointerStartX = null;

    if (Math.abs(distance) < 60) {
      return;
    }

    show(distance > 0 ? currentIndex - 1 : currentIndex + 1);
  });

  dialog.addEventListener('close', () => {
    image.removeAttribute('src');
    image.alt = '';
    caption.textContent = '';
    if (opener) {
      opener.focus();
    }
  });
})();
