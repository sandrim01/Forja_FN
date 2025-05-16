/**
 * Forja FN - Quiz System
 * Handles quiz timing, answers, and submissions
 */

let quizTimer;
let secondsRemaining;
let questionsAnswered = {};

document.addEventListener('DOMContentLoaded', function() {
    const quizContainer = document.getElementById('quizContainer');
    if (quizContainer) {
        initializeQuiz();
    }
});

/**
 * Initialize quiz functionality
 */
function initializeQuiz() {
    // Start timer if provided
    const timerElement = document.getElementById('quizTimer');
    if (timerElement) {
        const timeLimit = parseInt(timerElement.getAttribute('data-time-limit')) || 30;
        startQuizTimer(timeLimit * 60); // Convert minutes to seconds
    }
    
    // Set up answer selection
    setupAnswerSelection();
    
    // Set up form submission
    const quizForm = document.getElementById('quizForm');
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            if (!confirmQuizSubmission()) {
                e.preventDefault();
            }
        });
    }
}

/**
 * Start the quiz timer
 * @param {number} seconds - Total seconds for the quiz
 */
function startQuizTimer(seconds) {
    const timerElement = document.getElementById('quizTimer');
    secondsRemaining = seconds;
    
    updateTimerDisplay();
    
    quizTimer = setInterval(function() {
        secondsRemaining--;
        updateTimerDisplay();
        
        if (secondsRemaining <= 0) {
            clearInterval(quizTimer);
            alert('O tempo acabou! Suas respostas serão enviadas automaticamente.');
            document.getElementById('quizForm').submit();
        }
    }, 1000);
}

/**
 * Update the timer display
 */
function updateTimerDisplay() {
    const timerElement = document.getElementById('quizTimer');
    const minutes = Math.floor(secondsRemaining / 60);
    const seconds = secondsRemaining % 60;
    
    timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Change color to warn when less than 5 minutes remain
    if (secondsRemaining < 300) {
        timerElement.classList.add('text-danger');
    }
}

/**
 * Set up answer selection functionality
 */
function setupAnswerSelection() {
    const answerOptions = document.querySelectorAll('.answer-option');
    
    answerOptions.forEach(option => {
        option.addEventListener('click', function() {
            const questionId = this.getAttribute('data-question-id');
            const answerId = this.getAttribute('data-answer-id');
            
            // Remove selection from other options in the same question
            const questionOptions = document.querySelectorAll(`.answer-option[data-question-id="${questionId}"]`);
            questionOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to this option
            this.classList.add('selected');
            
            // Update hidden input
            const hiddenInput = document.querySelector(`input[name="answer_${questionId}"]`);
            if (hiddenInput) {
                hiddenInput.value = answerId;
            }
            
            // Track answered questions
            questionsAnswered[questionId] = true;
            updateProgress();
        });
    });
}

/**
 * Update progress indicator
 */
function updateProgress() {
    const totalQuestions = document.querySelectorAll('.question-card').length;
    const answeredCount = Object.keys(questionsAnswered).length;
    
    const progressElement = document.getElementById('quizProgress');
    if (progressElement) {
        const percentage = Math.floor((answeredCount / totalQuestions) * 100);
        progressElement.style.width = `${percentage}%`;
        progressElement.setAttribute('aria-valuenow', percentage);
        progressElement.textContent = `${answeredCount}/${totalQuestions}`;
    }
}

/**
 * Confirm quiz submission
 * @returns {boolean} - Whether to proceed with submission
 */
function confirmQuizSubmission() {
    const totalQuestions = document.querySelectorAll('.question-card').length;
    const answeredCount = Object.keys(questionsAnswered).length;
    
    if (answeredCount < totalQuestions) {
        return confirm(`Você respondeu apenas ${answeredCount} de ${totalQuestions} questões. Tem certeza que deseja enviar?`);
    }
    
    return true;
}

/**
 * Navigate to a specific question
 * @param {number} questionNumber - The question number to navigate to
 */
function navigateToQuestion(questionNumber) {
    const questionElement = document.getElementById(`question${questionNumber}`);
    if (questionElement) {
        questionElement.scrollIntoView({ behavior: 'smooth' });
    }
}
