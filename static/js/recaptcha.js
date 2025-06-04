/**
 * Robust reCAPTCHA Loader with Retry Mechanism
 * Handles network issues and ensures reCAPTCHA loads properly
 */

class ReCaptchaLoader {
    constructor(siteKey) {
        this.siteKey = siteKey;
        this.maxRetries = 5;
        this.retryDelay = 2000;
        this.currentRetry = 0;
        this.isLoaded = false;
        this.isLoading = false;
    }

    async load() {
        if (this.isLoaded || this.isLoading) {
            return;
        }

        if (!this.siteKey) {
            console.error('reCAPTCHA site key is missing');
            return;
        }

        this.isLoading = true;
        console.log(`Loading reCAPTCHA with site key: ${this.siteKey}`);

        try {
            await this.loadScript();
            this.isLoaded = true;
            this.isLoading = false;
            console.log('reCAPTCHA loaded successfully');
        } catch (error) {
            console.error('reCAPTCHA loading failed:', error);
            this.isLoading = false;
            
            if (this.currentRetry < this.maxRetries) {
                this.currentRetry++;
                console.log(`Retrying reCAPTCHA load (attempt ${this.currentRetry}/${this.maxRetries})`);
                setTimeout(() => this.load(), this.retryDelay);
            } else {
                console.error('reCAPTCHA loading failed after all retries');
                this.showFallbackMessage();
            }
        }
    }

    loadScript() {
        return new Promise((resolve, reject) => {
            // Remove any existing reCAPTCHA scripts
            const existingScripts = document.querySelectorAll('script[src*="recaptcha"]');
            existingScripts.forEach(script => script.remove());

            const script = document.createElement('script');
            script.src = `https://www.google.com/recaptcha/api.js?render=${this.siteKey}`;
            script.async = true;
            script.defer = true;

            script.onload = () => {
                // Wait for grecaptcha to be available
                const checkReady = () => {
                    if (window.grecaptcha && window.grecaptcha.ready) {
                        window.grecaptcha.ready(() => {
                            resolve();
                        });
                    } else {
                        setTimeout(checkReady, 100);
                    }
                };
                checkReady();
            };

            script.onerror = (error) => {
                reject(new Error('Failed to load reCAPTCHA script'));
            };

            // Add to head instead of body for better loading
            document.head.appendChild(script);

            // Set a timeout for the loading process
            setTimeout(() => {
                if (!this.isLoaded) {
                    reject(new Error('reCAPTCHA loading timeout'));
                }
            }, 10000);
        });
    }

    showFallbackMessage() {
        // Create a user-friendly message when reCAPTCHA fails
        const messageDiv = document.createElement('div');
        messageDiv.className = 'alert alert-warning mt-3';
        messageDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Connection Issue:</strong> Unable to load security verification. 
            Please check your internet connection and refresh the page.
        `;

        // Insert after forms that require reCAPTCHA
        const forms = document.querySelectorAll('form[data-requires-recaptcha="true"]');
        forms.forEach(form => {
            if (!form.querySelector('.recaptcha-error')) {
                messageDiv.classList.add('recaptcha-error');
                form.appendChild(messageDiv.cloneNode(true));
            }
        });
    }

    async executeRecaptcha(action = 'submit') {
        if (!this.isLoaded) {
            await this.load();
        }

        return new Promise((resolve, reject) => {
            if (window.grecaptcha && window.grecaptcha.ready) {
                window.grecaptcha.ready(() => {
                    window.grecaptcha.execute(this.siteKey, { action })
                        .then(token => resolve(token))
                        .catch(error => reject(error));
                });
            } else {
                reject(new Error('reCAPTCHA not available'));
            }
        });
    }
}

// Initialize reCAPTCHA when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Get site key from meta tag or global variable
    const siteKey = document.querySelector('meta[name="recaptcha-site-key"]')?.content ||
                   window.RECAPTCHA_SITE_KEY ||
                   '6LdD2VUrAAAAABG_Tt5fFYmWkRB4YFVHPdjggYzQ';

    if (siteKey && siteKey !== 'None') {
        window.recaptchaLoader = new ReCaptchaLoader(siteKey);
        window.recaptchaLoader.load();
    }
});

// Form submission handler with reCAPTCHA
function handleFormSubmission(form, action = 'submit') {
    if (!window.recaptchaLoader) {
        console.warn('reCAPTCHA loader not initialized');
        return Promise.resolve(null);
    }

    return window.recaptchaLoader.executeRecaptcha(action)
        .then(token => {
            // Add token to form
            let tokenInput = form.querySelector('input[name="g-recaptcha-response"]');
            if (!tokenInput) {
                tokenInput = document.createElement('input');
                tokenInput.type = 'hidden';
                tokenInput.name = 'g-recaptcha-response';
                form.appendChild(tokenInput);
            }
            tokenInput.value = token;
            return token;
        })
        .catch(error => {
            console.error('reCAPTCHA execution failed:', error);
            throw error;
        });
}

// Global function for form submissions
window.submitFormWithRecaptcha = function(form, action = 'submit') {
    return handleFormSubmission(form, action);
};