/**
 * reCAPTCHA v2 Integration with Enhanced Error Handling
 * Provides robust loading, retry mechanism, and fallback for network issues
 */

let recaptchaLoaded = false;
let loadAttempts = 0;
const maxRetries = 5;
const retryDelay = 2000; // 2 seconds

/**
 * Load reCAPTCHA v2 script dynamically with retry mechanism
 */
function loadRecaptcha() {
    return new Promise((resolve, reject) => {
        console.log(`Loading reCAPTCHA v2 with site key: ${window.recaptchaSiteKey}`);
        
        if (typeof grecaptcha !== 'undefined' && grecaptcha.render) {
            recaptchaLoaded = true;
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://www.google.com/recaptcha/api.js';
        script.async = true;
        script.defer = true;
        
        script.onload = () => {
            if (typeof grecaptcha !== 'undefined' && grecaptcha.render) {
                recaptchaLoaded = true;
                resolve();
            } else {
                reject(new Error('reCAPTCHA object not available after loading'));
            }
        };
        
        script.onerror = () => {
            reject(new Error('Failed to load reCAPTCHA script'));
        };
        
        // Set timeout for script loading
        setTimeout(() => {
            if (!recaptchaLoaded) {
                reject(new Error('reCAPTCHA loading timeout'));
            }
        }, 10000);
        
        document.head.appendChild(script);
    });
}

/**
 * Load reCAPTCHA with retry mechanism
 */
async function loadRecaptchaWithRetry() {
    while (loadAttempts < maxRetries && !recaptchaLoaded) {
        try {
            await loadRecaptcha();
            return true;
        } catch (error) {
            loadAttempts++;
            console.error('reCAPTCHA loading failed:', error);
            
            if (loadAttempts < maxRetries) {
                console.log(`Retrying reCAPTCHA load (attempt ${loadAttempts}/${maxRetries})`);
                await new Promise(resolve => setTimeout(resolve, retryDelay));
            }
        }
    }
    
    if (!recaptchaLoaded) {
        console.error('reCAPTCHA loading failed after all retries');
        showRecaptchaError('Unable to load security verification. Please check your internet connection and refresh the page.');
        return false;
    }
    
    return true;
}

/**
 * Render reCAPTCHA v2 widget
 */
function renderRecaptcha(containerId) {
    if (!recaptchaLoaded || typeof grecaptcha === 'undefined') {
        console.error('reCAPTCHA not loaded');
        return null;
    }
    
    try {
        return grecaptcha.render(containerId, {
            'sitekey': window.recaptchaSiteKey,
            'theme': 'light',
            'callback': function(response) {
                console.log('reCAPTCHA v2 completed');
                // Clear any error messages on successful completion
                const existingErrors = document.querySelectorAll('.recaptcha-error');
                existingErrors.forEach(error => error.remove());
            },
            'expired-callback': function() {
                console.log('reCAPTCHA v2 expired');
                showRecaptchaError('Security verification expired. Please complete it again.');
            },
            'error-callback': function() {
                console.log('reCAPTCHA v2 error');
                showRecaptchaError('Security verification failed. Please refresh the page and try again.');
            }
        });
    } catch (error) {
        console.error('Failed to render reCAPTCHA:', error);
        showRecaptchaError('Failed to load security verification. Please refresh the page.');
        return null;
    }
}

/**
 * Get reCAPTCHA v2 response
 */
function getRecaptchaResponse(widgetId) {
    if (!recaptchaLoaded || typeof grecaptcha === 'undefined') {
        return null;
    }
    
    if (widgetId !== undefined) {
        return grecaptcha.getResponse(widgetId);
    } else {
        return grecaptcha.getResponse();
    }
}

/**
 * Reset reCAPTCHA v2 widget
 */
function resetRecaptcha(widgetId) {
    if (!recaptchaLoaded || typeof grecaptcha === 'undefined') {
        return;
    }
    
    if (widgetId !== undefined) {
        grecaptcha.reset(widgetId);
    } else {
        grecaptcha.reset();
    }
}

/**
 * Show reCAPTCHA error message to user
 */
function showRecaptchaError(message) {
    // Remove any existing error messages
    const existingErrors = document.querySelectorAll('.recaptcha-error');
    existingErrors.forEach(error => error.remove());
    
    // Create new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-warning recaptcha-error mt-3';
    errorDiv.innerHTML = `
        <strong>Connection Issue:</strong> ${message}
    `;
    
    // Find the form and add error message
    const form = document.querySelector('form');
    if (form) {
        form.appendChild(errorDiv);
    }
}

/**
 * Validate reCAPTCHA v2 response on form submission
 */
function validateRecaptcha() {
    const response = getRecaptchaResponse();
    if (!response || response.length === 0) {
        showRecaptchaError('Please complete the security verification.');
        return false;
    }
    return true;
}

// Initialize reCAPTCHA when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Pre-load reCAPTCHA for better user experience
    loadRecaptchaWithRetry().then(() => {
        // Render reCAPTCHA widgets after loading
        const recaptchaContainers = document.querySelectorAll('.g-recaptcha');
        recaptchaContainers.forEach(container => {
            if (!container.hasChildNodes()) {
                renderRecaptcha(container.id || container);
            }
        });
    });
    
    // Handle form submissions
    const forms = document.querySelectorAll('form[data-recaptcha="true"]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateRecaptcha()) {
                e.preventDefault();
                return false;
            }
        });
    });
});

// Export functions for global access
window.recaptchaModule = {
    renderRecaptcha,
    getRecaptchaResponse,
    resetRecaptcha,
    validateRecaptcha,
    loadRecaptchaWithRetry
};