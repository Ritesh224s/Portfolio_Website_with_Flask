// Simple theme toggle (persists in localStorage)
(function(){
  const toggle = document.querySelector('#themeToggle');
  if(!toggle) return;
  const prefers = matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  const key = 'theme';
  const apply = t => document.documentElement.dataset.theme = t;
  apply(localStorage.getItem(key) || prefers);
  toggle.addEventListener('click', () => {
    const next = (document.documentElement.dataset.theme === 'dark') ? 'light' : 'dark';
    apply(next); localStorage.setItem(key, next);
  });
})();
