(function () {
  var banner = document.querySelector('[data-android-smart-banner]');
  if (!banner) return;

  // Tablets and desktop Android environments keep the normal page CTA instead.
  var userAgent = navigator.userAgent || '';
  var isAndroidPhone = /Android/i.test(userAgent) && !/Tablet|TV/i.test(userAgent) && Math.min(window.screen.width, window.screen.height) < 768;
  var storageKey = banner.getAttribute('data-banner-key');
  var dismissed = false;
  try {
    dismissed = localStorage.getItem(storageKey) === 'dismissed';
  } catch (error) {
    // Private browsing or restrictive settings should not prevent the page CTA.
  }
  if (!isAndroidPhone || !storageKey || dismissed) return;

  banner.hidden = false;
  document.body.classList.add('has-android-smart-banner');
  banner.querySelector('.android-smart-banner__dismiss').addEventListener('click', function () {
    try {
      localStorage.setItem(storageKey, 'dismissed');
    } catch (error) {
      // The banner still closes for this visit when storage is unavailable.
    }
    banner.hidden = true;
    document.body.classList.remove('has-android-smart-banner');
  });
}());
