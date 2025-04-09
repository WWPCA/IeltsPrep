/**
 * IELTS AI Prep - Practice Tests JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize practice test functionality
    const practiceTest = document.querySelector('.practice-test');
    if (practiceTest) {
        initializePracticeTest();
    }
    
    // Initialize the timer if needed
    const timerElement = document.getElementById('test-timer');
    if (timerElement) {
        const testType = timerElement.dataset.testType;
        let timeLimit;
        
        switch (testType) {
            case 'listening':
                timeLimit = 40 * 60; // 30 min test + 10 min transfer time
                break;
            case 'reading':
                timeLimit = 60 * 60; // 60 min
                break;
            case 'writing':
                timeLimit = 60 * 60; // 60 min
                break;
            default:
                timeLimit = 60 * 60; // Default 60 min
        }
        
        startTimer(timerElement, timeLimit);
    }
    
    // Add event listener to the form submission
    const testForm = document.getElementById('practice-test-form');
    if (testForm) {
        testForm.addEventListener('submit', submitTest);
    }
    
    // Initialize word counter for writing tests
    const writingTextarea = document.querySelector('.writing-textarea');
    if (writingTextarea) {
        initializeWordCounter(writingTextarea);
    }
    
    // Initialize audio player for listening tests
    const audioPlayer = document.getElementById('listening-audio');
    if (audioPlayer) {
        initializeAudioPlayer(audioPlayer);
    }
    
    // Check for offline mode and enable caching if needed
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(error => {
                console.error('ServiceWorker registration failed:', error);
            });
    }
    
    // Cache test data for offline use
    cacheTestDataForOffline();
});

/**
 * Initialize practice test functionality
 */
function initializePracticeTest() {
    // Add question numbering
    const questions = document.querySelectorAll('.question');
    questions.forEach((question, index) => {
        const questionNumber = document.createElement('span');
        questionNumber.className = 'question-number';
        questionNumber.textContent = `${index + 1}. `;
        
        const questionText = question.querySelector('.question-text');
        if (questionText) {
            questionText.prepend(questionNumber);
        }
    });
}

/**
 * Start the test timer
 */
function startTimer(timerElement, seconds) {
    let timeRemaining = seconds;
    
    // Update timer display
    function updateTimer() {
        timerElement.textContent = formatTime(timeRemaining);
        
        // Add warning class when less than 5 minutes remaining
        if (timeRemaining <= 300) {
            timerElement.classList.add('timer-warning');
        }
        
        // Add danger class when less than 1 minute remaining
        if (timeRemaining <= 60) {
            timerElement.classList.add('timer-danger');
        }
    }
    
    // Initial display
    updateTimer();
    
    // Update every second
    const timerInterval = setInterval(function() {
        timeRemaining--;
        updateTimer();
        
        // Save remaining time to localStorage for persistence
        localStorage.setItem('practiceTestTimeRemaining', timeRemaining);
        
        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            timerElement.textContent = 'Time\'s up!';
            
            // Auto-submit the test
            const testForm = document.getElementById('practice-test-form');
            if (testForm) {
                testForm.dispatchEvent(new Event('submit'));
            }
        }
    }, 1000);
    
    // Check if there's a previously saved timer
    const savedTime = localStorage.getItem('practiceTestTimeRemaining');
    if (savedTime) {
        timeRemaining = parseInt(savedTime);
        updateTimer();
    }
}

/**
 * Submit test answers
 */
function submitTest(event) {
    event.preventDefault();
    
    // Get test ID
    const testId = this.dataset.testId;
    
    // Collect all answers
    const answers = {};
    const answerInputs = document.querySelectorAll('.answer-input');
    
    answerInputs.forEach(input => {
        const questionId = input.dataset.questionId;
        const answer = input.value.trim();
        answers[questionId] = answer;
    });
    
    // Save answers to localStorage as backup
    saveAnswersToLocalStorage(testId, answers);
    
    // Check if we're offline
    if (!navigator.onLine) {
        showOfflineMessage();
        return;
    }
    
    // Submit answers to server
    fetch('/api/submit-test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            test_id: testId,
            answers: answers
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        displayTestResults(data);
        
        // Clear the timer and saved data
        localStorage.removeItem('practiceTestTimeRemaining');
        localStorage.removeItem(`testAnswers_${testId}`);
    })
    .catch(error => {
        console.error('Error submitting test:', error);
        saveTestForLater(testId, answers);
    });
}

/**
 * Save answers to localStorage for offline recovery
 */
function saveAnswersToLocalStorage(testId, answers) {
    localStorage.setItem(`testAnswers_${testId}`, JSON.stringify({
        testId: testId,
        answers: answers,
        date: new Date().toISOString()
    }));
}

/**
 * Save test for later submission when online
 */
function saveTestForLater(testId, answers) {
    const offlineTests = JSON.parse(localStorage.getItem('offlineTests') || '[]');
    
    offlineTests.push({
        testId: testId,
        answers: answers,
        date: new Date().toISOString()
    });
    
    localStorage.setItem('offlineTests', JSON.stringify(offlineTests));
    
    showOfflineMessage();
}

/**
 * Show offline message when test can't be submitted
 */
function showOfflineMessage() {
    const resultContainer = document.getElementById('test-results');
    if (resultContainer) {
        resultContainer.innerHTML = `
            <div class="alert alert-warning">
                <h4>You are currently offline</h4>
                <p>Your answers have been saved locally and will be submitted automatically when you're back online.</p>
                <p>You can safely leave this page and come back later.</p>
            </div>
        `;
    }
}

/**
 * Display test results
 */
function displayTestResults(data) {
    const resultContainer = document.getElementById('test-results');
    if (resultContainer) {
        resultContainer.innerHTML = `
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h3>Test Results</h3>
                </div>
                <div class="card-body">
                    <div class="score-circle">
                        <div class="score-number">${data.score.toFixed(1)}%</div>
                    </div>
                    <div class="score-details">
                        <p>You answered ${data.correct} out of ${data.total} questions correctly.</p>
                    </div>
                    <div class="mt-4">
                        <a href="/practice" class="btn btn-primary">Back to Practice Tests</a>
                    </div>
                </div>
            </div>
        `;
        
        // Scroll to results
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Initialize word counter for writing tests
 */
function initializeWordCounter(textarea) {
    const wordCountDisplay = document.getElementById('word-count');
    const minWords = parseInt(textarea.dataset.minWords || 0);
    
    function updateWordCount() {
        const text = textarea.value.trim();
        const wordCount = text ? text.split(/\s+/).length : 0;
        
        wordCountDisplay.textContent = `${wordCount} words`;
        
        // Add warning class if below minimum
        if (wordCount < minWords) {
            wordCountDisplay.className = 'word-count text-danger';
        } else {
            wordCountDisplay.className = 'word-count text-success';
        }
    }
    
    textarea.addEventListener('input', updateWordCount);
    updateWordCount(); // Initial count
}

/**
 * Initialize audio player for listening tests
 */
function initializeAudioPlayer(audioPlayer) {
    const playButton = document.getElementById('play-audio');
    const progressBar = document.getElementById('audio-progress');
    const currentTimeDisplay = document.getElementById('current-time');
    const durationDisplay = document.getElementById('duration');
    
    if (playButton && progressBar) {
        // Set up play/pause functionality
        playButton.addEventListener('click', function() {
            if (audioPlayer.paused) {
                audioPlayer.play();
                playButton.innerHTML = '<i class="fa fa-pause"></i> Pause';
            } else {
                audioPlayer.pause();
                playButton.innerHTML = '<i class="fa fa-play"></i> Play';
            }
        });
        
        // Update progress bar as audio plays
        audioPlayer.addEventListener('timeupdate', function() {
            const progress = (audioPlayer.currentTime / audioPlayer.duration) * 100;
            progressBar.value = progress;
            
            // Update time display
            currentTimeDisplay.textContent = formatTime(Math.floor(audioPlayer.currentTime));
        });
        
        // Enable seeking
        progressBar.addEventListener('input', function() {
            const seekTime = (progressBar.value / 100) * audioPlayer.duration;
            audioPlayer.currentTime = seekTime;
        });
        
        // Display duration when metadata is loaded
        audioPlayer.addEventListener('loadedmetadata', function() {
            durationDisplay.textContent = formatTime(Math.floor(audioPlayer.duration));
        });
        
        // Reset button when audio ends
        audioPlayer.addEventListener('ended', function() {
            playButton.innerHTML = '<i class="fa fa-play"></i> Play';
            progressBar.value = 0;
        });
        
        // Handle errors
        audioPlayer.addEventListener('error', function() {
            console.error('Error loading audio');
            playButton.disabled = true;
            playButton.textContent = 'Audio unavailable';
        });
    }
}

/**
 * Cache test data for offline use
 */
function cacheTestDataForOffline() {
    // Only cache if we're in an actual test
    const testForm = document.getElementById('practice-test-form');
    if (!testForm) {
        return;
    }
    
    const testId = testForm.dataset.testId;
    const testType = testForm.dataset.testType;
    
    // Get all test content
    const testContent = document.querySelector('.practice-test').innerHTML;
    
    // Save to localStorage
    localStorage.setItem(`cachedTest_${testId}`, JSON.stringify({
        id: testId,
        type: testType,
        content: testContent,
        cachedAt: new Date().toISOString()
    }));
    
    console.log(`Test ID ${testId} cached for offline use`);
    
    // If it's a listening test, try to cache the audio too
    const audioPlayer = document.getElementById('listening-audio');
    if (audioPlayer && audioPlayer.src) {
        cacheAudioForOffline(audioPlayer.src, testId);
    }
}

/**
 * Cache audio for offline listening tests
 */
function cacheAudioForOffline(audioUrl, testId) {
    // Only proceed if Cache API is available
    if ('caches' in window) {
        caches.open('ielts-prep-audio-cache').then(cache => {
            cache.add(audioUrl).then(() => {
                console.log(`Audio for test ID ${testId} cached for offline use`);
            }).catch(error => {
                console.error('Failed to cache audio:', error);
            });
        });
    }
}
