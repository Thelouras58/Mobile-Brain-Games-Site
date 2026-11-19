(() => {
  const ua = navigator.userAgent || '';
  const touch = navigator.maxTouchPoints > 0;
  const shortSide = Math.min(screen.width, screen.height);
  const ipad = /iPad/i.test(ua) || (/Macintosh/i.test(ua) && touch);
  const androidTablet = /Android/i.test(ua) && !/Mobile/i.test(ua);
  // Screen dimensions keep landscape phones blocked, even in desktop mode.
  const smallTouchScreen = touch && shortSide > 0 && shortSide < 600;
  const phone = /iPhone|iPod|Windows Phone/i.test(ua) || smallTouchScreen ||
    (!ipad && !androidTablet && (/Mobi/i.test(ua) || navigator.userAgentData?.mobile === true));
  if (phone) {
    document.getElementById('game-shell').hidden = true;
    document.getElementById('game-guide').hidden = true;
    document.getElementById('mobile-message').hidden = false;
    return;
  }
  const loading = document.getElementById('loading');
  function retry(text) {
    loading.innerHTML = '';
    const box = document.createElement('div');
    const message = document.createElement('p');
    message.textContent = text;
    const button = document.createElement('button');
    button.textContent = 'Retry';
    button.onclick = () => location.reload();
    box.append(message, button);
    loading.append(box);
  }
  const timer = setTimeout(() => retry('Still loading Flame…'), 30000);
  window.addEventListener('flutter-first-frame', () => {
    clearTimeout(timer);
    loading.remove();
  }, {once: true});
  const script = document.createElement('script');
  script.src = 'flutter_bootstrap.js';
  script.async = true;
  script.onerror = () => {
    clearTimeout(timer);
    retry('Flame could not load. Check your connection and retry.');
  };
  document.body.append(script);
})();
