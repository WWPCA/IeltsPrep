/**
 * Assessment Recovery Module
 * 
 * This module provides functionality to detect connection issues during assessments
 * and allow users to restart assessments if their internet connection drops.
 */

// Online/offline status tracking
let wasOffline = false;
let currentTestId = null;
let currentTestType = null;
let recoveryAttempted = false;
let sessionMonitorInterval = null;

// Initialize the recovery system
function initAssessmentRecovery(testId, testType) {
    currentTestId = testId;
    currentTestType = testType;
    
    // Check if we were in the middle of a session
    checkForUnfinishedSession();
    
    // Setup connection monitoring
    setupConnectionMonitoring();
    
    // Periodically ping the server to keep the session alive
    startSessionMonitor();
}

// Check if there was an unfinished session for this test
function checkForUnfinishedSession() {
    if (!currentTestId || recoveryAttempted) return;
    
    // Check for unfinished sessions via API
    fetch(`/${currentTestType}/recovery_check/${currentTestId}`)
        .then(response => response.json())
        .then(data => {
            if (data.has_unfinished_session) {
                // Show the recovery dialog
                showRecoveryDialog(data.started_at);
            }
        })
        .catch(error => {
            console.error('Error checking for unfinished sessions:', error);
        });
    
    // Mark that we've attempted recovery
    recoveryAttempted = true;
}

// Show a dialog asking if the user wants to restart their session
function showRecoveryDialog(startedAt) {
    // Create dialog if it doesn't exist
    if (!document.getElementById('recovery-dialog')) {
        const dialog = document.createElement('div');
        dialog.id = 'recovery-dialog';
        dialog.className = 'modal fade';
        dialog.setAttribute('tabindex', '-1');
        dialog.setAttribute('role', 'dialog');
        dialog.setAttribute('aria-labelledby', 'recoveryModalLabel');
        dialog.setAttribute('aria-hidden', 'true');
        
        // Format the time
        const startTime = new Date(startedAt);
        const timeString = startTime.toLocaleString();
        
        dialog.innerHTML = `
            <div class="modal-dialog" role="document">
                <div class="modal-content">
                    <div class="modal-header bg-warning">
                        <h5 class="modal-title" id="recoveryModalLabel">Session Recovery</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                        <p>It looks like you were in the middle of an assessment that was interrupted due to a connection issue.</p>
                        <p>Your previous session started at ${timeString}.</p>
                        <p>Would you like to restart this assessment from the beginning?</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">No, cancel</button>
                        <button type="button" class="btn btn-primary" id="restart-session-btn">Yes, restart assessment</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        // Add event listener for the restart button
        document.getElementById('restart-session-btn').addEventListener('click', function() {
            // Reload the page to restart the assessment
            window.location.reload();
        });
    }
    
    // Show the dialog using Bootstrap's modal functionality
    $('#recovery-dialog').modal('show');
}

// Setup monitoring for connection changes
function setupConnectionMonitoring() {
    // Initial status
    wasOffline = !navigator.onLine;
    
    // Listen for online/offline events
    window.addEventListener('online', handleConnectionChange);
    window.addEventListener('offline', handleConnectionChange);
}

// Handle connection status changes
function handleConnectionChange(event) {
    if (event.type === 'offline') {
        // We've gone offline
        wasOffline = true;
        
        // Show a notification that we're offline
        showOfflineNotification();
    } else if (event.type === 'online' && wasOffline) {
        // We've come back online after being offline
        wasOffline = false;
        
        // Show a notification that we're back online
        showOnlineNotification();
        
        // Check if we need to recover a session
        checkForUnfinishedSession();
    }
}

// Show a notification that we're offline
function showOfflineNotification() {
    const notification = document.createElement('div');
    notification.className = 'alert alert-warning alert-dismissible fade show fixed-top mx-auto';
    notification.style.width = '80%';
    notification.style.maxWidth = '500px';
    notification.style.marginTop = '20px';
    notification.style.zIndex = '9999';
    notification.setAttribute('role', 'alert');
    
    notification.innerHTML = `
        <strong>You are offline!</strong> Your internet connection has been lost.
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 10 seconds
    setTimeout(() => {
        notification.remove();
    }, 10000);
}

// Show a notification that we're back online
function showOnlineNotification() {
    const notification = document.createElement('div');
    notification.className = 'alert alert-success alert-dismissible fade show fixed-top mx-auto';
    notification.style.width = '80%';
    notification.style.maxWidth = '500px';
    notification.style.marginTop = '20px';
    notification.style.zIndex = '9999';
    notification.setAttribute('role', 'alert');
    
    notification.innerHTML = `
        <strong>You are back online!</strong> Your internet connection has been restored.
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 10 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Periodically ping the server to keep the session alive
function startSessionMonitor() {
    // Clear any existing interval
    if (sessionMonitorInterval) {
        clearInterval(sessionMonitorInterval);
    }
    
    // Set up a new ping every 60 seconds
    sessionMonitorInterval = setInterval(() => {
        // Only ping if we're online
        if (navigator.onLine) {
            fetch('/ping')
                .catch(error => {
                    console.log('Ping failed:', error);
                });
        }
    }, 60000); // Every 60 seconds
}

// Clean up when leaving the page
function cleanupAssessmentRecovery() {
    window.removeEventListener('online', handleConnectionChange);
    window.removeEventListener('offline', handleConnectionChange);
    
    if (sessionMonitorInterval) {
        clearInterval(sessionMonitorInterval);
    }
}

// Export functions for usage in pages
window.AssessmentRecovery = {
    init: initAssessmentRecovery,
    cleanup: cleanupAssessmentRecovery
};