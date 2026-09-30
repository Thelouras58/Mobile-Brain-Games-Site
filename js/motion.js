(function () {
  var pending = new Set();
  var imageCleanups = [];
  var observer;
  var stopped = false;
  var downloadCount = document.querySelector('[data-download-count]');
  var countFrame;
  var waitingToCount = document.hidden;

  function finishCount() {
    if (countFrame !== undefined) window.cancelAnimationFrame(countFrame);
    if (downloadCount) downloadCount.textContent = '80K+';
  }

  function startCount() {
    if (!downloadCount) return;
    if (document.hidden) {
      waitingToCount = true;
      return;
    }
    waitingToCount = false;
    finishCount();
    downloadCount.classList.remove('download-count--complete');
    var countStart;
    downloadCount.textContent = '0K+';
    function countDownloads(timestamp) {
      if (document.hidden) {
        finishCount();
        return;
      }
      if (countStart === undefined) countStart = timestamp;
      var progress = Math.min((timestamp - countStart) / 1200, 1);
      downloadCount.textContent = Math.round(80 * progress) + 'K+';
      if (progress < 1) {
        countFrame = window.requestAnimationFrame(countDownloads);
      } else {
        downloadCount.classList.add('download-count--complete');
      }
    }
    countFrame = window.requestAnimationFrame(countDownloads);
  }

  startCount();
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) finishCount();
    else if (waitingToCount) startCount();
  });

  function inViewport(element) {
    var bounds = element.getBoundingClientRect();
    return bounds.bottom > 0 && bounds.top < window.innerHeight;
  }

  function clearImageFades(element) {
    element.querySelectorAll('.motion-image-fade').forEach(function (image) {
      image.classList.remove('motion-image-fade');
    });
  }

  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting || !pending.has(entry.target)) return;
        pending.delete(entry.target);
        observer.unobserve(entry.target);
        if (stopped) return;
        clearImageFades(entry.target);
        entry.target.classList.add('motion-reveal');
      });
    }, { threshold: 0 });

    document.querySelectorAll('[data-reveal]').forEach(function (element) {
      // Above-the-fold content and a restored scroll position remain still.
      if (inViewport(element)) return;
      pending.add(element);
      observer.observe(element);
    });
  }

  document.querySelectorAll('[data-image-fade]').forEach(function (image) {
    if (image.complete) return;

    function cleanup() {
      image.removeEventListener('load', loaded);
      image.removeEventListener('error', cleanup);
    }

    function loaded() {
      cleanup();
      var component = image.closest('[data-reveal]');
      // A component entrance takes precedence over its image's fade.
      if (stopped || !image.naturalWidth || !inViewport(image) ||
          (component && (pending.has(component) || component.classList.contains('motion-reveal')))) return;
      image.classList.add('motion-image-fade');
    }

    image.addEventListener('load', loaded);
    image.addEventListener('error', cleanup);
    imageCleanups.push(cleanup);
  });

  document.addEventListener('animationend', function (event) {
    if (event.animationName === 'mbg-reveal') event.target.classList.remove('motion-reveal');
    if (event.animationName === 'mbg-image-fade') event.target.classList.remove('motion-image-fade');
  });

  document.addEventListener('focusin', function (event) {
    var component = event.target.closest('[data-reveal]');
    if (!component) return;
    pending.delete(component);
    if (observer) observer.unobserve(component);
    component.classList.remove('motion-reveal');
    clearImageFades(component);
  });

  function stopMotion() {
    stopped = true;
    finishCount();
    if (observer) observer.disconnect();
    pending.clear();
    imageCleanups.forEach(function (cleanup) { cleanup(); });
    document.querySelectorAll('.motion-reveal,.motion-image-fade').forEach(function (element) {
      element.classList.remove('motion-reveal', 'motion-image-fade');
    });
  }

  window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
      stopMotion();
      startCount();
    }
  });
}());
