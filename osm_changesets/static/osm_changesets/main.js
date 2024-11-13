(() => {
  function show(el) {
    el.classList.remove(CLASS_HIDDEN);
  }

  function hide(el) {
    el.classList.add(CLASS_HIDDEN);
  }

  function reloadImages() {
    const loadingImages = images.filter(img => !img.naturalWidth);
    if (loadingImages.length) {
      progressEl.textContent =
        ((images.length - loadingImages.length) / images.length) * 100 + '%';
      hide(headingEl);
      show(loadingEl);
      loadingImages.forEach(img => {
        const origSrc = img.getAttribute('src');
        const newSrc = origSrc.replace(/(#.*|$)/, '#' + new Date().getTime());
        img.setAttribute('src', newSrc);
      });
      setTimeout(reloadImages, 2000);
    } else {
      hide(loadingEl);
      show(headingEl);
      clearInterval(spinnerInterval);
    }
  }

  const CLASS_HIDDEN = 'hidden';

  const headingEl = document.querySelector('h1');
  const loadingEl = document.getElementById('loading');
  const progressEl = document.getElementById('progress');
  const spinnerEl = document.getElementById('spinner');

  const images = Array.from(document.querySelectorAll('img'));

  document.body.classList.add('js');

  const frames = ['.  ', '.. ', '...', ' ..', '  .', '   '];
  let i = 0;
  const spinnerInterval = setInterval(function () {
    spinnerEl.innerHTML = frames[i];
    i = (i + 1) % frames.length;
  }, 300);

  setTimeout(reloadImages, 500);
})();
