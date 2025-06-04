/**
 * reCAPTCHA v3 Integration with Enhanced Error Handling
 * Provides robust loading, retry mechanism, and fallback for network issues
 */

// Prevent variable redeclaration if script is loaded multiple times
if (typeof window.recaptchaLoaded === 'undefined') {
    window.recaptchaLoaded = false;
    window.loadAttempts = 0;
    window.maxRetries = 5;
    window.retryDelay = 2000; // 2 seconds
}

/**
 * Load reCAPTCHA v2 script dynamically with retry mechanism
 */
function loadRecaptcha() {
    return new Promise((resolve, reject) => {
        console.log(`Loading reCAPTCHA v2 with site key: ${window.recaptchaSiteKey}`);
        
        if (typeof grecaptcha !== 'undefined' && grecaptcha.render) {
            window.recaptchaLoaded = true;
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://www.google.com/recaptcha/api.js';
        script.async = true;
        script.defer = true;
        
        script.onload = () => {
            if (typeof grecaptcha !== 'undefined' && grecaptcha.render) {
                window.recaptchaLoaded = true;
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
            if (!window.recaptchaLoaded) {
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
    while (window.loadAttempts < window.maxRetries && !window.recaptchaLoaded) {
        try {
            await loadRecaptcha();
            return true;
        } catch (error) {
            window.loadAttempts++;
            console.error('reCAPTCHA loading failed:', error);
            
            if (window.loadAttempts < window.maxRetries) {
                console.log(`Retrying reCAPTCHA load (attempt ${window.loadAttempts}/${window.maxRetries})`);
                await new Promise(resolve => setTimeout(resolve, window.retryDelay));
            }
        }
    }
    
    if (!window.recaptchaLoaded) {
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
    if (!window.recaptchaLoaded || typeof grecaptcha === 'undefined') {
        console.error('reCAPTCHA not loaded');
        return null;
    }
    
    if (!window.recaptchaSiteKey) {
        console.error('reCAPTCHA site key not available');
        showRecaptchaError('Security verification configuration error. Please refresh the page.');
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
    if (!window.recaptchaLoaded || typeof grecaptcha === 'undefined') {
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
    if (!window.recaptchaLoaded || typeof grecaptcha === 'undefined') {
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
    // Skip if already initialized
    if (window.recaptchaInitialized) {
        return;
    }
    window.recaptchaInitialized = true;
    
    // Pre-load reCAPTCHA for better user experience
    loadRecaptchaWithRetry().then(() => {
        // Render reCAPTCHA widgets after loading
        const recaptchaContainers = document.querySelectorAll('.g-recaptcha');
        recaptchaContainers.forEach(container => {
            if (!container.hasChildNodes() && container.id) {
                renderRecaptcha(container.id);
            } else if (!container.hasChildNodes()) {
                // Create unique ID if none exists
                const uniqueId = 'recaptcha-' + Math.random().toString(36).substr(2, 9);
                container.id = uniqueId;
                renderRecaptcha(uniqueId);
            }
        });
    }).catch(error => {
        console.error('Failed to initialize reCAPTCHA:', error);
        showRecaptchaError('Failed to load security verification. Please refresh the page.');
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