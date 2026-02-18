/* ExecSignals — main.js */
(function() {
  'use strict';

  // ─── Mobile menu toggle ───
  var menuToggle = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.nav');
  if (menuToggle && nav) {
    menuToggle.addEventListener('click', function() {
      var isActive = nav.classList.toggle('mobile-active');
      menuToggle.classList.toggle('active', isActive);
      document.body.style.overflow = isActive ? 'hidden' : '';
    });
    // Close on nav link click
    nav.addEventListener('click', function(e) {
      if (e.target.tagName === 'A') {
        nav.classList.remove('mobile-active');
        menuToggle.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  // ─── Smooth scroll for anchor links ───
  document.querySelectorAll('a[href^="#"]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // ─── Animate signal bars on scroll ───
  var signalBars = document.getElementById('signal-bars');
  if (signalBars) {
    var barObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.querySelectorAll('.signal-bar-fill').forEach(function(bar) {
            bar.style.width = bar.dataset.width + '%';
          });
          barObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });
    barObserver.observe(signalBars);
  }

  // ─── Animate hero stat counter ───
  var statLeads = document.getElementById('stat-leads');
  if (statLeads) {
    var target = parseInt(statLeads.textContent, 10) || 272;
    var duration = 1500;
    var start = performance.now();
    function tick(now) {
      var progress = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      statLeads.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // ─── CTA form handler ───
  var ctaBtn = document.getElementById('cta-btn');
  var ctaEmail = document.getElementById('cta-email');
  var ctaForm = document.getElementById('cta-form');
  var ctaSuccess = document.getElementById('cta-success');

  if (ctaBtn && ctaEmail) {
    ctaBtn.addEventListener('click', function() {
      var email = ctaEmail.value.trim();
      if (!email || !email.includes('@') || !email.includes('.')) {
        ctaEmail.style.borderColor = 'var(--error)';
        return;
      }

      ctaBtn.disabled = true;
      ctaBtn.textContent = 'Sending...';

      // POST to server endpoint (Phase 2: replace with real endpoint)
      // For now, store locally and show success
      var sub = {
        email: email,
        product: 'execsignals',
        timestamp: new Date().toISOString()
      };

      // TODO Phase 2: Replace with fetch() POST to server endpoint
      // fetch('https://api.execsignals.com/subscribe', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(sub)
      // })
      // .then(function(r) { return r.json(); })
      // .then(function(data) { showSuccess(); })
      // .catch(function(err) { showError(); });

      // Temporary: localStorage fallback
      try {
        var subs = JSON.parse(localStorage.getItem('execsignals_subscribers') || '[]');
        subs.push(sub);
        localStorage.setItem('execsignals_subscribers', JSON.stringify(subs));
      } catch(e) {}

      showSuccess();

      // GA4 event
      if (typeof gtag === 'function') {
        gtag('event', 'form_submit', {
          event_category: 'cta',
          event_label: 'monday_brief_signup'
        });
      }
    });

    ctaEmail.addEventListener('focus', function() {
      this.style.borderColor = 'var(--accent)';
    });
  }

  function showSuccess() {
    if (ctaForm) ctaForm.style.display = 'none';
    var finePrint = document.querySelector('.cta-fine-print');
    if (finePrint) finePrint.style.display = 'none';
    if (ctaSuccess) ctaSuccess.style.display = 'block';
  }

  // ─── Blur overlay CTA scroll ───
  document.querySelectorAll('.blur-overlay-cta').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var cta = document.getElementById('cta-section');
      if (cta) cta.scrollIntoView({ behavior: 'smooth' });
    });
  });

  // ─── GA4 custom events ───
  if (typeof gtag === 'function') {
    // Track CTA clicks
    document.querySelectorAll('.nav-cta, .blur-overlay-cta, .cta-btn, .ep-cta-link').forEach(function(el) {
      el.addEventListener('click', function() {
        gtag('event', 'cta_click', {
          event_category: 'engagement',
          event_label: el.className || el.textContent.trim().substring(0, 30)
        });
      });
    });

    // Track pricing section view
    var pricingSection = document.getElementById('pricing');
    if (pricingSection) {
      var pricingObserver = new IntersectionObserver(function(entries) {
        if (entries[0].isIntersecting) {
          gtag('event', 'view_pricing', { event_category: 'engagement' });
          pricingObserver.unobserve(pricingSection);
        }
      }, { threshold: 0.5 });
      pricingObserver.observe(pricingSection);
    }

    // Track scroll depth
    var scrollMilestones = [25, 50, 75, 100];
    var reached = {};
    window.addEventListener('scroll', function() {
      var scrollPct = Math.round(
        (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
      );
      scrollMilestones.forEach(function(m) {
        if (scrollPct >= m && !reached[m]) {
          reached[m] = true;
          gtag('event', 'scroll_depth', {
            event_category: 'engagement',
            event_label: m + '%',
            value: m
          });
        }
      });
    }, { passive: true });
  }

})();
