/* =========================================================
   Grand Prestige Hotel System - JS Helpers
   ========================================================= */

(function () {
  'use strict';

  // ── Highlight active sidebar link ──
  try {
    const path = window.location.pathname;
    document.querySelectorAll('.side-links a').forEach(a => {
      const href = a.getAttribute('href') || '';
      if (href && path !== '/' && path.startsWith(href.replace(/\/$/, ''))) {
        a.classList.add('active');
      }
    });
  } catch (e) {}

  // ── Auto-dismiss flash alerts after 6 seconds ──
  try {
    setTimeout(() => {
      document.querySelectorAll('.alert').forEach(el => {
        el.style.transition = 'opacity .5s, transform .5s';
        el.style.opacity = '0';
        el.style.transform = 'translateY(-6px)';
        setTimeout(() => el.remove(), 500);
      });
    }, 6000);
  } catch (e) {}

  // ── OTP input: auto-format (numbers only) ──
  try {
    const otpInput = document.querySelector('input[name="otp"]');
    if (otpInput) {
      otpInput.addEventListener('input', () => {
        otpInput.value = otpInput.value.replace(/\D/g, '').slice(0, 6);
      });
    }
  } catch (e) {}

  // ── Auto-logout after 10 minutes of inactivity ──
  const IDLE_MS = 10 * 60 * 1000;
  let lastActivity = Date.now();

  function resetTimer() { lastActivity = Date.now(); }
  ['click', 'keydown', 'mousemove', 'scroll', 'touchstart'].forEach(ev => {
    window.addEventListener(ev, resetTimer, { passive: true });
  });

  setInterval(() => {
    // Only auto-logout if user is logged in (logout link exists)
    const logoutLink = document.querySelector('a[href*="logout"]');
    if (!logoutLink) return;
    if (Date.now() - lastActivity > IDLE_MS) {
      window.location.href = logoutLink.href;
    }
  }, 15000);

  // ── Smooth button feedback ──
  try {
    document.querySelectorAll('button[type="submit"]').forEach(btn => {
      btn.addEventListener('click', function () {
        const orig = this.textContent;
        this.textContent = 'Processing…';
        this.style.opacity = '0.75';
        setTimeout(() => {
          this.textContent = orig;
          this.style.opacity = '';
        }, 3000);
      });
    });
  } catch (e) {}

})();
