(function () {
  var button = document.querySelector('.menu-toggle');
  var nav = document.getElementById('site-nav');
  if (!button || !nav) return;

  var mobile = window.matchMedia('(max-width: 900px)');

  function setOpen(open) {
    var shouldOpen = mobile.matches && open;
    button.setAttribute('aria-expanded', String(shouldOpen));
    button.setAttribute('aria-label', shouldOpen ? '关闭导航' : '打开导航');
    nav.hidden = mobile.matches && !shouldOpen;
    if (!shouldOpen && document.activeElement && nav.contains(document.activeElement)) button.focus();
  }

  function updateNavigation() {
    document.body.classList.add('nav-ready');
    setOpen(false);
  }

  nav.hidden = mobile.matches;
  document.body.classList.add('nav-ready');
  button.addEventListener('click', function () {
    setOpen(button.getAttribute('aria-expanded') !== 'true');
  });
  nav.addEventListener('click', function (event) {
    if (event.target.closest('a')) setOpen(false);
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
      setOpen(false);
      button.focus();
    }
  });
  document.addEventListener('click', function (event) {
    if (mobile.matches && button.getAttribute('aria-expanded') === 'true' &&
        !nav.contains(event.target) && !button.contains(event.target)) setOpen(false);
  });
  mobile.addEventListener('change', updateNavigation);
})();
