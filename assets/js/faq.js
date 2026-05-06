// XToolsPro3 LP — minimal interactivity
// 1) Reveal-on-scroll (respects prefers-reduced-motion)
// 2) Native <details> handles FAQ accordion; here we only auto-close siblings.

(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- Reveal-on-scroll ----------------------------------------------------
  if (!reduce && 'IntersectionObserver' in window) {
    const targets = document.querySelectorAll(
      '.hero-copy, .hero-visual, .pain-card, .why-card, .feat-card, .metric, .plan, .addon, .review-grid figure, .dev-grid > *, .qa, .final-cta'
    );
    targets.forEach(el => el.classList.add('reveal'));
    const io = new IntersectionObserver((entries, obs) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('reveal-in');
          obs.unobserve(e.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach(el => io.observe(el));
  }

  // ---- FAQ: open one at a time --------------------------------------------
  const faqGroup = document.querySelectorAll('.faq .qa');
  faqGroup.forEach(d => {
    d.addEventListener('toggle', () => {
      if (d.open) faqGroup.forEach(o => { if (o !== d) o.open = false; });
    });
  });
})();
