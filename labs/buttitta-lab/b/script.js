(function () {
  var root = document.documentElement;
  var key = 'lab-theme';
  function apply(t) { root.setAttribute('data-theme', t); try { localStorage.setItem(key, t); } catch (e) {} }
  var saved = null; try { saved = localStorage.getItem(key); } catch (e) {}
  if (saved) apply(saved);
  else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) root.setAttribute('data-theme', 'dark');
  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('.theme-btn');
    if (btn) btn.addEventListener('click', function () {
      apply(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });
    var tog = document.querySelector('.nav-toggle');
    var menu = document.querySelector('.menu');
    if (tog && menu) tog.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      tog.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    // publication filter (if present)
    var q = document.querySelector('#pubsearch');
    if (q) q.addEventListener('input', function () {
      var v = q.value.toLowerCase();
      document.querySelectorAll('.pub').forEach(function (li) {
        li.style.display = li.textContent.toLowerCase().indexOf(v) > -1 ? '' : 'none';
      });
      document.querySelectorAll('.year-head').forEach(function (h) {
        var next = h.nextElementSibling; var any = false;
        if (next) next.querySelectorAll('.pub').forEach(function (li) { if (li.style.display !== 'none') any = true; });
        h.style.display = any ? '' : 'none';
      });
    });
  });
})();
