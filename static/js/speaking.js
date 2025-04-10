/**
 * IELTS AI Prep - Speaking Assessment JavaScript
 * 
 * This file handles the speaking assessment functionality with audio recording
 * and submission for analysis. It uses a namespace pattern to avoid conflicts
 * with global variables in other JavaScript files.
 */

// Create a namespace for all speaking assessment variables and functions
const speakingModule = {
    // Recording state variables
    mediaRecorder: null,
    audioChunks: [],
    recordingTimer: null,
    recordingSeconds: 0,
    isRecording: false,
    
    // Format time function for the speaking module (mm:ss format)
    formatTime: function(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize speaking assessment
    const speakingTest = document.querySelector('.speaking-test');
    if (speakingTest) {
        initializeSpeakingTest();
    }
});

/**
 * Initialize the speaking test functionality
 */
function initializeSpeakingTest() {
    const recordButton = document.getElementById('record-button');
    const stopButton = document.getElementById('stop-button');
    const timerDisplay = document.getElementById('record-time');
    const feedbackContainer = document.getElementById('feedback-container');
    const promptId = document.querySelector('.speaking-test').dataset.promptId;
    
    if (recordButton && stopButton) {
        // Request microphone access
        recordButton.addEventListener('click', function() {
            // Disable button while requesting permission
            recordButton.disabled = true;
            recordButton.textContent = 'Requesting microphone...';
            
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    // Re-enable button
                    recordButton.disabled = false;
                    recordButton.textContent = 'Start Recording';
                    
                    // Setup recorder with the stream
                    setupRecorder(stream);
                    
                    // Add click handlers
                    recordButton.addEventListener('click', startRecording);
                    stopButton.addEventListener('click', stopRecording);
                })
                .catch(error => {
                    console.error('Error accessing microphone:', error);
                    recordButton.disabled = true;
                    recordButton.textContent = 'Microphone access denied';
                    
                    // Show error message
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'alert alert-danger mt-3';
                    errorMsg.textContent = 'Microphone access is required for the speaking assessment. Please allow microphone access in your browser settings and refresh the page.';
                    recordButton.parentNode.appendChild(errorMsg);
                });
        });
        
        // Setup feedback submission
        const submitFeedbackButton = document.getElementById('submit-feedback');
        if (submitFeedbackButton) {
            submitFeedbackButton.addEventListener('click', function() {
                submitSpeakingRecording(promptId);
            });
        }
    }
    
    /**
     * Set up the media recorder with the audio stream
     */
    function setupRecorder(stream) {
        speakingModule.mediaRecorder = new MediaRecorder(stream);
        
        speakingModule.mediaRecorder.ondataavailable = function(event) {
            speakingModule.audioChunks.push(event.data);
        };
        
        speakingModule.mediaRecorder.onstop = function() {
            // Create audio blob
            const audioBlob = new Blob(speakingModule.audioChunks, { type: 'audio/mp3' });
            
            // Create a URL for the blob
            const audioUrl = URL.createObjectURL(audioBlob);
            
            // Display playback controls
            displayAudioPlayback(audioUrl);
            
            // Save blob for submission
            window.recordedAudioBlob = audioBlob;
        };
    }
    
    /**
     * Start recording audio
     */
    function startRecording() {
        // Clear any existing recording
        speakingModule.audioChunks = [];
        speakingModule.recordingSeconds = 0;
        
        // Hide any previous feedback
        if (feedbackContainer) {
            feedbackContainer.innerHTML = '';
            feedbackContainer.style.display = 'none';
        }
        
        // Update UI
        recordButton.disabled = true;
        stopButton.disabled = false;
        timerDisplay.textContent = '00:00';
        timerDisplay.style.display = 'inline';
        
        // Start recording
        speakingModule.mediaRecorder.start();
        speakingModule.isRecording = true;
        
        // Start timer
        speakingModule.recordingTimer = setInterval(function() {
            speakingModule.recordingSeconds++;
            timerDisplay.textContent = speakingModule.formatTime(speakingModule.recordingSeconds);
            
            // Auto-stop after 2 minutes (IELTS speaking responses are typically 1-2 minutes)
            if (speakingModule.recordingSeconds >= 120) {
                stopRecording();
            }
        }, 1000);
        
        console.log('Recording started');
    }
    
    /**
     * Stop recording audio
     */
    function stopRecording() {
        if (!speakingModule.isRecording) return;
        
        // Stop the recorder
        speakingModule.mediaRecorder.stop();
        speakingModule.isRecording = false;
        
        // Stop the timer
        clearInterval(speakingModule.recordingTimer);
        
        // Update UI
        recordButton.disabled = false;
        stopButton.disabled = true;
        
        console.log('Recording stopped');
    }
    
    /**
     * Display audio playback controls after recording
     */
    function displayAudioPlayback(audioUrl) {
        const playbackContainer = document.getElementById('audio-playback');
        if (playbackContainer) {
            playbackContainer.innerHTML = `
                <div class="card mt-3">
                    <div class="card-header">
                        <h4>Your Recording (${speakingModule.formatTime(speakingModule.recordingSeconds)})</h4>
                    </div>
                    <div class="card-body">
                        <audio controls src="${audioUrl}" class="w-100"></audio>
                        <div class="d-flex justify-content-between mt-3">
                            <button id="re-record-button" class="btn btn-secondary">
                                <i class="fa fa-redo"></i> Record Again
                            </button>
                            <button id="submit-feedback" class="btn btn-primary">
                                <i class="fa fa-paper-plane"></i> Get Feedback
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            // Add re-record button handler
            document.getElementById('re-record-button').addEventListener('click', function() {
                playbackContainer.innerHTML = '';
                window.recordedAudioBlob = null;
            });
            
            // Add submit button handler
            document.getElementById('submit-feedback').addEventListener('click', function() {
                submitSpeakingRecording(promptId);
            });
        }
    }
}

/**
 * Submit the speaking recording for analysis
 */
function submitSpeakingRecording(promptId) {
    if (!window.recordedAudioBlob) {
        console.error('No recording available');
        return;
    }
    
    // Show loading state
    const feedbackContainer = document.getElementById('feedback-container');
    feedbackContainer.style.display = 'block';
    feedbackContainer.innerHTML = `
        <div class="card mt-4">
            <div class="card-body text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Analyzing your speaking response...</p>
                <p class="small text-muted">This may take up to 30 seconds.</p>
            </div>
        </div>
    `;
    
    // Create form data for upload
    const formData = new FormData();
    formData.append('prompt_id', promptId);
    formData.append('audio', window.recordedAudioBlob, 'recording.mp3');
    
    // Check if we're offline
    if (!navigator.onLine) {
        showOfflineFeedback();
        return;
    }
    
    // Submit recording to server
    fetch('/api/speaking/submit', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        displayFeedback(data);
    })
    .catch(error => {
        console.error('Error submitting recording:', error);
        showErrorFeedback();
    });
}

/**
 * Display speaking assessment feedback
 */
function displayFeedback(data) {
    const feedbackContainer = document.getElementById('feedback-container');
    if (!feedbackContainer) return;
    
    // Format scores for display
    const scores = data.scores;
    
    feedbackContainer.innerHTML = `
        <div class="card mt-4">
            <div class="card-header bg-primary text-white">
                <h3>Speaking Assessment Results</h3>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4 text-center">
                        <div class="score-circle">
                            <div class="score-number">${scores.overall}</div>
                            <div class="score-label">Overall Band</div>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <h4>Detailed Scores</h4>
                        <div class="score-bars">
                            <div class="score-bar">
                                <div class="score-label">Fluency & Coherence</div>
                                <div class="progress">
                                    <div class="progress-bar" role="progressbar" style="width: ${scores.fluency/9*100}%" 
                                        aria-valuenow="${scores.fluency}" aria-valuemin="0" aria-valuemax="9">
                                        ${scores.fluency}
                                    </div>
                                </div>
                            </div>
                            <div class="score-bar">
                                <div class="score-label">Lexical Resource</div>
                                <div class="progress">
                                    <div class="progress-bar" role="progressbar" style="width: ${scores.vocabulary/9*100}%" 
                                        aria-valuenow="${scores.vocabulary}" aria-valuemin="0" aria-valuemax="9">
                                        ${scores.vocabulary}
                                    </div>
                                </div>
                            </div>
                            <div class="score-bar">
                                <div class="score-label">Grammar Range & Accuracy</div>
                                <div class="progress">
                                    <div class="progress-bar" role="progressbar" style="width: ${scores.grammar/9*100}%" 
                                        aria-valuenow="${scores.grammar}" aria-valuemin="0" aria-valuemax="9">
                                        ${scores.grammar}
                                    </div>
                                </div>
                            </div>
                            <div class="score-bar">
                                <div class="score-label">Pronunciation</div>
                                <div class="progress">
                                    <div class="progress-bar" role="progressbar" style="width: ${scores.pronunciation/9*100}%" 
                                        aria-valuenow="${scores.pronunciation}" aria-valuemin="0" aria-valuemax="9">
                                        ${scores.pronunciation}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <h4>Transcription</h4>
                    <div class="transcription-box p-3 bg-light">
                        ${data.transcription}
                    </div>
                </div>
                
                <div class="mt-4">
                    <h4>Detailed Feedback</h4>
                    <div class="feedback-text">
                        ${data.feedback.replace(/\n/g, '<br>')}
                    </div>
                </div>
                
                ${data.feedback_audio_url ? `
                <div class="mt-4">
                    <h4>Audio Feedback</h4>
                    <audio controls src="${data.feedback_audio_url}" class="w-100"></audio>
                    <p class="small text-muted mt-2">Listen to your feedback. This can help you improve your listening skills as well!</p>
                </div>
                ` : ''}
                
                <div class="mt-4 text-center">
                    <a href="/speaking" class="btn btn-primary">Try Another Prompt</a>
                </div>
            </div>
        </div>
    `;
}

/**
 * Show offline feedback message
 */
function showOfflineFeedback() {
    const feedbackContainer = document.getElementById('feedback-container');
    if (feedbackContainer) {
        feedbackContainer.innerHTML = `
            <div class="alert alert-warning">
                <h4>You are currently offline</h4>
                <p>Speaking assessment requires an internet connection. Please connect to the internet and try again.</p>
                <p>Your recording has been saved and will be available when you reconnect.</p>
            </div>
        `;
    }
}

/**
 * Show error feedback message
 */
function showErrorFeedback() {
    const feedbackContainer = document.getElementById('feedback-container');
    if (feedbackContainer) {
        feedbackContainer.innerHTML = `
            <div class="alert alert-danger">
                <h4>Error Processing Recording</h4>
                <p>We encountered an error while analyzing your speaking response. Please try again.</p>
                <p>If the problem persists, please try a different browser or device.</p>
                <button class="btn btn-primary mt-3" onclick="window.location.reload()">Reload Page</button>
            </div>
        `;
    }
}
