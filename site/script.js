/* HargaRumah portfolio - vanilla scroll reveal + copy hint.
   No window.scroll listener. IntersectionObserver only. */

(() => {
  'use strict';

  // Honor reduced motion - no-op if user prefers reduced motion
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Reveal on intersect
  const targets = document.querySelectorAll('.reveal');
  if (!targets.length) return;

  if (reduce) {
    targets.forEach((el) => el.classList.add('in'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
  );

  targets.forEach((el) => observer.observe(el));

  // Smooth scroll for in-page anchor CTAs (fallback for browsers without CSS smooth)
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href');
      if (!id || id === '#') return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
})();
