(function () {
  var header = document.getElementById('header');
  var menuButton = document.querySelector('.menu-toggle');
  var nav = document.getElementById('site-nav');
  var navLinks = document.querySelectorAll('.site-nav a');

  function closeMenu() {
    document.body.classList.remove('menu-open');
    if (menuButton) menuButton.setAttribute('aria-expanded', 'false');
  }

  if (menuButton) {
    menuButton.addEventListener('click', function () {
      var isOpen = document.body.classList.toggle('menu-open');
      menuButton.setAttribute('aria-expanded', String(isOpen));
    });
  }

  navLinks.forEach(function (link) {
    link.addEventListener('click', closeMenu);
  });

  document.addEventListener('click', function (event) {
    if (document.body.classList.contains('menu-open') && !nav.contains(event.target) && !menuButton.contains(event.target)) {
      closeMenu();
    }
  });

  function updateHeader() {
    header.classList.toggle('is-scrolled', window.scrollY > 24);
  }

  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });
})();
