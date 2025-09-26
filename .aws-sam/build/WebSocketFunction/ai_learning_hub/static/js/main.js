/**
 * AI Learning Hub - Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Module toggles in learning interface
    const moduleHeaders = document.querySelectorAll('.module-header');
    if (moduleHeaders.length > 0) {
        moduleHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const moduleItem = this.closest('.module-item');
                const lessonList = moduleItem.querySelector('.lesson-list');
                
                // Toggle the current module
                lessonList.classList.toggle('active');
                this.querySelector('.module-toggle i').classList.toggle('fa-chevron-down');
                this.querySelector('.module-toggle i').classList.toggle('fa-chevron-up');
            });
        });
    }
    
    // Lesson completion
    const completeButtons = document.querySelectorAll('.complete-lesson-btn');
    if (completeButtons.length > 0) {
        completeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const lessonId = this.getAttribute('data-lesson-id');
                const courseId = this.getAttribute('data-course-id');
                
                fetch('/api/complete-lesson', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        lesson_id: lessonId,
                        course_id: courseId
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update UI
                        this.innerHTML = '<i class="fas fa-check-circle me-2"></i>Completed';
                        this.classList.remove('btn-primary');
                        this.classList.add('btn-success');
                        this.disabled = true;
                        
                        // Update progress bar
                        const progressBar = document.querySelector('.course-progress-bar');
                        if (progressBar) {
                            progressBar.style.width = data.completion_percentage + '%';
                            progressBar.setAttribute('aria-valuenow', data.completion_percentage);
                            
                            document.querySelector('.progress-percentage').textContent = 
                                Math.round(data.completion_percentage) + '%';
                        }
                        
                        // Mark lesson as completed in sidebar
                        const lessonItem = document.querySelector(`.lesson-item[data-lesson-id="${lessonId}"]`);
                        if (lessonItem) {
                            lessonItem.classList.add('completed');
                        }
                        
                        // If course is completed, show success message
                        if (data.is_completed) {
                            const completionAlert = document.createElement('div');
                            completionAlert.className = 'alert alert-success mt-4';
                            completionAlert.innerHTML = `
                                <h4 class="alert-heading"><i class="fas fa-trophy me-2"></i>Congratulations!</h4>
                                <p>You've completed this course! Continue your learning journey with related courses or projects.</p>
                                <hr>
                                <div class="d-flex justify-content-end">
                                    <a href="/dashboard" class="btn btn-sm btn-success me-2">Go to Dashboard</a>
                                    <a href="/courses" class="btn btn-sm btn-primary">Explore More Courses</a>
                                </div>
                            `;
                            
                            document.querySelector('.lesson-content').appendChild(completionAlert);
                        }
                        
                        // Show Next Lesson Button
                        const nextButton = document.querySelector('.next-lesson-btn');
                        if (nextButton) {
                            nextButton.classList.remove('d-none');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        });
    }
    
    // Quiz submission
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const quizId = this.getAttribute('data-quiz-id');
            const courseId = this.getAttribute('data-course-id');
            const lessonId = this.getAttribute('data-lesson-id');
            
            // Convert form data to JSON
            const answers = {};
            const questions = document.querySelectorAll('.quiz-question');
            
            questions.forEach(question => {
                const questionId = question.getAttribute('data-question-id');
                const questionType = question.getAttribute('data-question-type');
                
                if (questionType === 'multiple_choice') {
                    const selected = formData.get(`question_${questionId}`);
                    if (selected) {
                        answers[questionId] = selected;
                    }
                } else if (questionType === 'true_false') {
                    const selected = formData.get(`question_${questionId}`);
                    if (selected) {
                        answers[questionId] = selected;
                    }
                } else if (questionType === 'code_completion') {
                    const code = document.querySelector(`#code_answer_${questionId}`).value;
                    answers[questionId] = code;
                }
            });
            
            fetch('/api/submit-quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    quiz_id: quizId,
                    course_id: courseId,
                    lesson_id: lessonId,
                    answers: answers
                })
            })
            .then(response => response.json())
            .then(data => {
                // Display results
                const resultDiv = document.getElementById('quiz-results');
                if (resultDiv) {
                    let resultHtml = `
                        <div class="card mb-4">
                            <div class="card-header bg-${data.passed ? 'success' : 'warning'} text-white">
                                <h4 class="mb-0">
                                    <i class="fas fa-${data.passed ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                                    Quiz Results: ${Math.round(data.percentage)}%
                                </h4>
                            </div>
                            <div class="card-body">
                                <p>You scored ${data.score} out of ${data.total} points.</p>
                    `;
                    
                    if (data.passed) {
                        resultHtml += `
                            <div class="alert alert-success">
                                <p class="mb-0"><i class="fas fa-trophy me-2"></i>Congratulations! You've passed this quiz and this lesson has been marked as completed.</p>
                            </div>
                            <div class="text-end">
                                <a href="#" class="btn btn-primary continue-btn">Continue to Next Lesson</a>
                            </div>
                        `;
                    } else {
                        resultHtml += `
                            <div class="alert alert-warning">
                                <p class="mb-0"><i class="fas fa-info-circle me-2"></i>You need to score at least 70% to pass this quiz and complete the lesson.</p>
                            </div>
                            <div class="text-end">
                                <button class="btn btn-primary retry-quiz-btn">Try Again</button>
                            </div>
                        `;
                    }
                    
                    resultHtml += `</div></div>`;
                    
                    resultDiv.innerHTML = resultHtml;
                    resultDiv.scrollIntoView({ behavior: 'smooth' });
                    
                    // Disable form
                    document.querySelectorAll('#quiz-form input, #quiz-form button').forEach(el => {
                        el.disabled = true;
                    });
                    
                    // Handle retry button
                    const retryButton = document.querySelector('.retry-quiz-btn');
                    if (retryButton) {
                        retryButton.addEventListener('click', function() {
                            // Reset form
                            quizForm.reset();
                            
                            // Enable form elements
                            document.querySelectorAll('#quiz-form input, #quiz-form button').forEach(el => {
                                el.disabled = false;
                            });
                            
                            // Clear results
                            resultDiv.innerHTML = '';
                        });
                    }
                    
                    // Update progress if passed
                    if (data.passed) {
                        // Update progress bar
                        const progressBar = document.querySelector('.course-progress-bar');
                        if (progressBar) {
                            fetch('/api/complete-lesson', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    lesson_id: lessonId,
                                    course_id: courseId
                                })
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.success) {
                                    progressBar.style.width = data.completion_percentage + '%';
                                    progressBar.setAttribute('aria-valuenow', data.completion_percentage);
                                    
                                    document.querySelector('.progress-percentage').textContent = 
                                        Math.round(data.completion_percentage) + '%';
                                    
                                    // Mark lesson as completed in sidebar
                                    const lessonItem = document.querySelector(`.lesson-item[data-lesson-id="${lessonId}"]`);
                                    if (lessonItem) {
                                        lessonItem.classList.add('completed');
                                    }
                                }
                            });
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length > 0) {
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
});

// Function to toggle mobile menu
function toggleMobileMenu() {
    const mobileMenu = document.querySelector('.navbar-collapse');
    mobileMenu.classList.toggle('show');
}