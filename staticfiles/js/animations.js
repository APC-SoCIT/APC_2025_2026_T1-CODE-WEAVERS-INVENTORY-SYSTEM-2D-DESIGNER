// Page Load Animation
document.addEventListener('DOMContentLoaded', () => {
  document.body.classList.add('loaded');

  // Initialize AOS
  AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Add loading animation to buttons
  const buttons = document.querySelectorAll('button[type="submit"]');
  buttons.forEach(button => {
    button.addEventListener('click', function() {
      if (!this.classList.contains('loading')) {
        this.classList.add('loading');
        const originalText = this.innerHTML;
        this.innerHTML = '<span class="spinner"></span> Loading...';

        // Remove loading state after action completes
        setTimeout(() => {
          this.classList.remove('loading');
          this.innerHTML = originalText;
        }, 2000);
      }
    });
  });

  // Add hover animation to cards
  const cards = document.querySelectorAll('.product-card');
  cards.forEach(card => {
    card.addEventListener('mouseenter', function(e) {
      const bounds = this.getBoundingClientRect();
      const mouseX = e.clientX - bounds.left;
      const mouseY = e.clientY - bounds.top;

      this.style.setProperty('--mouse-x', `${mouseX}px`);
      this.style.setProperty('--mouse-y', `${mouseY}px`);
    });
  });

  // Add toast notification system
  window.showToast = function(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <i class="toast-icon fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span class="toast-message">${message}</span>
      </div>
      <div class="toast-progress"></div>
    `;

    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 100);

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  };

  // Add image lazy loading with blur effect
  const lazyImages = document.querySelectorAll('img[data-src]');
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.add('loaded');
        observer.unobserve(img);
      }
    });
  });

  lazyImages.forEach(img => imageObserver.observe(img));

  // Add smooth counter animation
  function animateCounter(element, target) {
    const duration = 1000;
    const steps = 50;
    const stepDuration = duration / steps;
    const stepSize = target / steps;
    let current = 0;
    let step = 0;

    const timer = setInterval(() => {
      current += stepSize;
      step++;
      element.textContent = Math.round(current);

      if (step >= steps) {
        element.textContent = target;
        clearInterval(timer);
      }
    }, stepDuration);
  }

  // Initialize counters when they come into view
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = parseInt(entry.target.dataset.target);
        animateCounter(entry.target, target);
        counterObserver.unobserve(entry.target);
      }
    });
  });

  document.querySelectorAll('.counter').forEach(counter => {
    counterObserver.observe(counter);
  });
});