(function () {
  'use strict';
  window.mbgDesktopWebPlayEligible = function () {
    var ua = navigator.userAgent || '';
    var mobile = /Android|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini|Mobile/i.test(ua);
    var tablet = /iPad|Tablet|PlayBook|Silk/i.test(ua) || (/Macintosh/i.test(ua) && navigator.maxTouchPoints > 1);
    return !mobile && !tablet && matchMedia('(hover: hover) and (pointer: fine)').matches;
  };
  function update() {
    var allowed = window.mbgDesktopWebPlayEligible();
    document.querySelectorAll('[data-desktop-web-play]').forEach(function (link) { link.hidden = !allowed; });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', update, { once: true });
  else update();
  matchMedia('(hover: hover) and (pointer: fine)').addEventListener('change', update);
})();
