/**
 * Comprehensive Assessment Recovery System
 * 
 * Protects users from losing their one assessment opportunity due to:
 * - Network outages/choppy internet
 * - Accidental browser/tab closure
 * - System crashes or user errors
 */

// Recovery state tracking
let wasOffline = false;
let currentTestId = null;
let currentTestType = null;
let recoveryAttempted = false;
let sessionMonitorInterval = null;
let progressSaveInterval = null;
let hasUnsavedProgress = false;
let lastProgressSave = null;

// Initialize the comprehensive recovery system
function initAssessmentRecovery(testId, testType) {
    currentTestId = testId;
    currentTestType = testType;
    
    // Check if we were in the middle of a session
    checkForUnfinishedSession();
    
    // Setup connection monitoring
    setupConnectionMonitoring();
    
    // Protect against accidental browser closure
    setupBrowserCloseProtection();
    
    // Auto-save progress every 30 seconds
    setupAutoProgressSave();
    
    // Periodically ping the server to keep the session alive
    startSessionMonitor();
    
    // Show recovery notification
    showRecoveryProtectionNotice();
}

// Protect against accidental browser/tab closure
function setupBrowserCloseProtection() {
    // Warn user before closing browser/tab
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedProgress) {
            const message = 'You have an assessment in progress. Are you sure you want to leave? Your progress will be saved and you can resume later.';
            e.preventDefault();
            e.returnValue = message;
            return message;
        }
    });
    
    // Handle page visibility changes (user switches tabs, minimizes browser)
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Save progress when user leaves the page
            saveCurrentProgress('page_hidden');
        } else {
            // Check connection when user returns
            checkConnectionStatus();
        }
    });
}

// Auto-save progress every 30 seconds
function setupAutoProgressSave() {
    progressSaveInterval = setInterval(function() {
        if (hasUnsavedProgress) {
            saveCurrentProgress('auto_save');
        }
    }, 30000); // Save every 30 seconds
}

// Save current assessment progress
function saveCurrentProgress(reason = 'manual') {
    if (!currentTestId) return;
    
    const progressData = {
        timestamp: new Date().toISOString(),
        reason: reason,
        current_part: getCurrentAssessmentPart(),
        responses: gatherCurrentResponses(),
        time_spent: getTimeSpent(),
        browser_info: {
            userAgent: navigator.userAgent,
            online: navigator.onLine
        }
    };
    
    // Save to server
    fetch(`/assessment/recovery/checkpoint/${currentTestId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(progressData)
    }).then(response => {
        if (response.ok) {
            lastProgressSave = new Date();
            hasUnsavedProgress = false;
            updateProgressIndicator('saved');
        }
    }).catch(error => {
        console.error('Failed to save progress:', error);
        updateProgressIndicator('error');
    });
    
    // Also save to local storage as backup
    localStorage.setItem(`assessment_backup_${currentTestId}`, JSON.stringify(progressData));
}

// Show recovery protection notice
function showRecoveryProtectionNotice() {
    const notice = document.createElement('div');
    notice.className = 'alert alert-info alert-dismissible fade show position-fixed';
    notice.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 350px;';
    notice.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-shield-alt text-primary me-2"></i>
            <div>
                <strong>Assessment Protection Active</strong>
                <small class="d-block text-muted">Your progress is automatically saved. If interrupted, you can resume where you left off.</small>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notice);
    
    // Auto-dismiss after 8 seconds
    setTimeout(() => {
        if (notice.parentNode) {
            notice.remove();
        }
    }, 8000);
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
        
        // Log the disconnection event
        logConnectionIssue('disconnect');
    } else if (event.type === 'online' && wasOffline) {
        // We've come back online after being offline
        wasOffline = false;
        
        // Show a notification that we're back online
        showOnlineNotification();
        
        // Log the reconnection event
        logConnectionIssue('reconnect');
        
        // Check if we need to recover a session
        checkForUnfinishedSession();
    }
}

// Log connection issues to the server
function logConnectionIssue(issueType) {
    // Only log if we have a test ID
    if (!currentTestId) return;
    
    // Gather connection information
    const connectionInfo = {
        effectiveType: navigator.connection ? navigator.connection.effectiveType : 'unknown',
        downlink: navigator.connection ? navigator.connection.downlink : 'unknown',
        rtt: navigator.connection ? navigator.connection.rtt : 'unknown',
        online: navigator.onLine,
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        devicePixelRatio: window.devicePixelRatio,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        userLocalTime: new Date().toString()
    };
    
    // Send the log data to the server
    fetch('/api/log_connection_issue', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            issue_type: issueType,
            test_id: currentTestId,
            test_type: currentTestType,
            connection_info: connectionInfo,
            user_local_time: new Date().toString()
        })
    }).catch(error => {
        // If we can't log the issue, just record it in console - we're likely offline
        console.error('Failed to log connection issue:', error);
    });
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