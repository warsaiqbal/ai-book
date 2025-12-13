// Accessibility features for WCAG 2.1 AA compliance
// This implementation enhances the Docusaurus site for accessibility

// 1. Keyboard navigation enhancement
document.addEventListener('DOMContentLoaded', function() {
  // Add focus indicators to all focusable elements
  addFocusIndicators();
  
  // Ensure all interactive elements are keyboard accessible
  makeKeyboardAccessible();
  
  // Add ARIA attributes where needed
  addAriaAttributes();
});

// Function to add visible focus indicators
function addFocusIndicators() {
  // Add focus styles via JavaScript if not available in CSS
  const style = document.createElement('style');
  style.textContent = `
    a:focus,
    button:focus,
    input:focus,
    select:focus,
    textarea:focus,
    [tabindex]:focus {
      outline: 2px solid #4c78f0;
      outline-offset: 2px;
    }
  `;
  document.head.appendChild(style);
}

// Ensure interactive elements are keyboard accessible
function makeKeyboardAccessible() {
  // Add tabIndex to elements that should be focusable but aren't by default
  const clickableElements = document.querySelectorAll('.clickable, [data-clickable]');
  clickableElements.forEach(el => {
    if (!el.getAttribute('tabindex')) {
      el.setAttribute('tabindex', '0');
    }
  });
}

// Add appropriate ARIA attributes
function addAriaAttributes() {
  // Add labels to form elements without explicit labels
  const inputs = document.querySelectorAll('input, textarea, select');
  inputs.forEach(input => {
    if (!input.getAttribute('aria-label') && !input.getAttribute('aria-labelledby')) {
      const associatedLabel = document.querySelector(`label[for="${input.id}"]`);
      if (!associatedLabel && input.placeholder) {
        input.setAttribute('aria-label', input.placeholder);
      }
    }
  });
  
  // Add ARIA roles to landmark elements
  const mainContent = document.querySelector('main');
  if (mainContent && !mainContent.getAttribute('role')) {
    mainContent.setAttribute('role', 'main');
  }
  
  // Add skip navigation link for screen readers
  addSkipNavigationLink();
}

// Add a "skip to content" link for keyboard users
function addSkipNavigationLink() {
  const skipLink = document.createElement('a');
  skipLink.href = '#main-content';
  skipLink.textContent = 'Skip to main content';
  skipLink.id = 'skip-link';
  skipLink.style.cssText = `
    position: absolute;
    top: -40px;
    left: 6px;
    color: #fff;
    background: #000;
    padding: 8px;
    z-index: 1000;
    text-decoration: none;
  `;
  skipLink.style.left = '6px';
  
  skipLink.addEventListener('focus', () => {
    skipLink.style.top = '6px';
  });
  
  skipLink.addEventListener('blur', () => {
    skipLink.style.top = '-40px';
  });
  
  if (document.body) {
    document.body.insertBefore(skipLink, document.body.firstChild);
  }
}

// Adjust color contrast if needed
function ensureColorContrast() {
  // This would typically run contrast analysis on the page
  // and potentially adjust colors to meet WCAG 2.1 AA standards
}

// Support for reduced motion
function addReducedMotionSupport() {
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  
  if (prefersReducedMotion.matches) {
    // Disable animations if user prefers reduced motion
    const style = document.createElement('style');
    style.textContent = `
      *,
      *::before,
      *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    `;
    document.head.appendChild(style);
  }
  
  // Listen for changes to the preference
  prefersReducedMotion.addEventListener('change', addReducedMotionSupport);
}

// Initialize accessibility enhancements
addReducedMotionSupport();