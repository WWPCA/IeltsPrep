/**
 * IELTS GenAI Prep - Error Suppressor
 * Handles unwanted error messages without affecting preview window
 */

// Only run error suppression if not in preview mode
if (!window.location.href.includes('preview.')) {
  function suppressErrors() {
    const fixedElements = document.querySelectorAll(
      'div[style*="position:fixed"], ' +
      'div[style*="position: fixed"], ' +
      'div[style*="bottom:"], ' +
      'div[style*="right:"], ' +
      'div[style*="z-index: 9"]'
    );

    fixedElements.forEach(function(el) {
      if (el.textContent && (
          el.textContent.includes('ERROR') || 
          el.textContent.includes('Invalid details') ||
          el.textContent.includes('Error') ||
          el.textContent.includes('error')
        )) {
        el.style.display = 'none';
        el.style.visibility = 'hidden';
        el.style.opacity = '0';
        el.style.pointerEvents = 'none';
        el.remove();
      }
    });
    
    // Also find all elements that have fixed or absolute positioning
    document.querySelectorAll('div').forEach(function(el) {
      if (el.style && (
        (el.style.position === 'fixed' || el.style.position === 'absolute') &&
        (el.style.bottom === '0' || el.style.bottom === '0px' || 
         el.style.bottom === '10px' || el.style.bottom === '20px' ||
         el.style.right === '0' || el.style.right === '0px' ||
         el.style.right === '10px' || el.style.right === '20px')
      )) {
        console.log('Error Suppressor: Removing fixed position element');
        el.style.display = 'none';
        el.style.visibility = 'hidden';
        el.style.opacity = '0';
        el.style.pointerEvents = 'none';
        el.remove();
      }
    });
    
    // Also find elements with error classes
    const errorElements = document.querySelectorAll('.alert-danger, .alert-error, .text-danger');
    
    errorElements.forEach(function(el) {
      // Only remove unexpected/unwanted error messages
      if (el.textContent && (
          el.textContent.includes('ERROR') || 
          el.textContent.includes('Invalid details') ||
          el.textContent.includes('Error') ||
          el.textContent.includes('error')
        )) {
        // Avoid removing legitimate validation messages
        if (!el.closest('.password-feedback') && 
            !el.closest('.confirm-feedback') &&
            !el.closest('form')) {
          console.log('Error Suppressor: Removing error element with class:', el.className);
          el.style.display = 'none';
          el.style.visibility = 'hidden';
          el.style.opacity = '0';
          el.style.pointerEvents = 'none';
          el.remove();
        }
      }
    });
    
    // Check for toast-like elements positioned at the bottom
    const bottomElements = document.querySelectorAll('div[style*="bottom: "], div[style*="bottom:"]');
    
    bottomElements.forEach(function(el) {
      // Only target error messages
      if (el.textContent && (
          el.textContent.includes('ERROR') || 
          el.textContent.includes('Invalid details') ||
          el.textContent.includes('Error') ||
          el.textContent.includes('error')
        )) {
        console.log('Error Suppressor: Removing bottom-positioned element:', el.textContent);
        el.style.display = 'none';
        el.style.visibility = 'hidden';
        el.style.opacity = '0';
        el.style.pointerEvents = 'none';
        el.remove();
      }
    });
  }

  // Run error suppression periodically
  setInterval(suppressErrors, 1000);
  
    // Also override any window error or console error handling
    const originalConsoleError = console.error;
    console.error = function() {
      // Only log to console, don't display visually
      originalConsoleError.apply(console, arguments);
    };
    
    // Override window.onerror
    window.onerror = function(message, source, lineno, colno, error) {
      // Just consume the error to prevent default handling
      console.log('Error suppressor caught window error:', message);
      return true; // Prevents default error handling
    };
}