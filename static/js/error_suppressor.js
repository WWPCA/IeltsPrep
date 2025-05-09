/**
 * IELTS GenAI Prep - Error Suppressor
 * 
 * This script aggressively removes unwanted "ERROR: Invalid details" messages
 * that appear in the bottom-right corner of certain pages.
 */

// Add a special inline tag to the head to execute immediate suppression
document.write('<script id="error-suppressor-preload">'+
  'function quickSuppressErrors() {'+
    'var errors = document.querySelectorAll("div[style*=\\"position:fixed\\"], div[style*=\\"position: fixed\\"]");'+
    'for(var i=0; i<errors.length; i++) {'+
      'if(errors[i].textContent && (errors[i].textContent.includes("ERROR") || errors[i].textContent.includes("Invalid details"))) {'+
        'errors[i].remove();'+
      '}'+
    '}'+
  '}'+
  'setInterval(quickSuppressErrors, 50);'+
'</script>');

(function() {
  // Run immediately before DOM content loaded
  suppressErrors();

  // Also run when DOM is loaded
  document.addEventListener('DOMContentLoaded', function() {
    suppressErrors();
    
    // Set interval to repeatedly check and remove errors
    setInterval(suppressErrors, 100); // Check very frequently (every 100ms)
  });

  // Function to suppress unwanted error messages
  function suppressErrors() {
    // Find all fixed-position elements
    const fixedElements = document.querySelectorAll('div[style*="position:fixed"], div[style*="position: fixed"]');
    
    fixedElements.forEach(function(el) {
      // Check if the element contains error text
      if (el.textContent && (
          el.textContent.includes('ERROR') || 
          el.textContent.includes('Invalid details') ||
          el.textContent.includes('Error')
        )) {
        console.log('Error Suppressor: Removing unwanted error message:', el.textContent);
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
          el.textContent.includes('Error')
        )) {
        // Avoid removing legitimate validation messages
        if (!el.closest('.password-feedback') && 
            !el.closest('.confirm-feedback') &&
            !el.closest('form')) {
          console.log('Error Suppressor: Removing error element with class:', el.className);
          el.remove();
        }
      }
    });
    
    // Check for and remove any elements with inline style containing "bottom: 0"
    // which is often used for notification toast messages
    const bottomElements = document.querySelectorAll('div[style*="bottom: 0"], div[style*="bottom:0"]');
    
    bottomElements.forEach(function(el) {
      // Only target error messages
      if (el.textContent && (
          el.textContent.includes('ERROR') || 
          el.textContent.includes('Invalid details') ||
          el.textContent.includes('Error')
        )) {
        console.log('Error Suppressor: Removing bottom-positioned element:', el.textContent);
        el.remove();
      }
    });
  }
})();