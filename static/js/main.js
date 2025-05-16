/**
 * Forja FN - Main JavaScript File
 * Contains core functionality for the platform
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Flash message auto-close
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const alert = new bootstrap.Alert(message);
            alert.close();
        }, 5000);
    });

    // Level up notification
    checkForLevelUp();

    // Initialize mobile menu
    setupMobileMenu();

    // Update timestamp displays
    updateTimestamps();
});

/**
 * Check if user has leveled up and display notification
 */
function checkForLevelUp() {
    const levelUpContainer = document.getElementById('levelUpContainer');
    if (levelUpContainer && localStorage.getItem('leveledUp') === 'true') {
        levelUpContainer.classList.remove('d-none');
        localStorage.removeItem('leveledUp');

        // Hide after 5 seconds
        setTimeout(() => {
            levelUpContainer.classList.add('fade-out');
            setTimeout(() => {
                levelUpContainer.classList.add('d-none');
            }, 1000);
        }, 5000);
    }
}

/**
 * Update XP and check for level up
 * @param {number} xpGained - Amount of XP gained
 */
function updateXP(xpGained) {
    // Make AJAX request to update XP
    fetch('/api/check_xp')
        .then(response => response.json())
        .then(data => {
            // Update XP display
            const xpDisplay = document.getElementById('userXP');
            if (xpDisplay) {
                xpDisplay.textContent = data.xp;
            }

            // Update progress bar
            const progressBar = document.querySelector('.xp-progress');
            if (progressBar) {
                const percentage = (data.xp / data.next_level_xp) * 100;
                progressBar.style.width = `${Math.min(100, percentage)}%`;
            }

            // Update level display
            const levelDisplay = document.getElementById('userLevel');
            if (levelDisplay && levelDisplay.textContent != data.level) {
                // Level up!
                levelDisplay.textContent = data.level;
                localStorage.setItem('leveledUp', 'true');
                
                // Update rank name and image
                const rankNameElement = document.getElementById('rankName');
                if (rankNameElement) {
                    rankNameElement.textContent = data.rank_name;
                }
                
                const rankImageElement = document.getElementById('rankImage');
                if (rankImageElement) {
                    rankImageElement.src = data.rank_image;
                }
                
                // Reload page to show level up notification
                window.location.reload();
            }
        })
        .catch(error => console.error('Error updating XP:', error));
}

/**
 * Initialize mobile menu behavior
 */
function setupMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        document.addEventListener('click', (event) => {
            const isClickInside = navbarToggler.contains(event.target) || navbarCollapse.contains(event.target);
            
            if (!isClickInside && navbarCollapse.classList.contains('show')) {
                // Close the navbar if clicked outside
                const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                bsCollapse.hide();
            }
        });
    }
}

/**
 * Format relative timestamps
 */
function updateTimestamps() {
    const timestamps = document.querySelectorAll('.relative-time');
    
    timestamps.forEach(element => {
        const timestamp = new Date(element.getAttribute('data-timestamp'));
        const now = new Date();
        const diffInSeconds = Math.floor((now - timestamp) / 1000);
        
        let formattedTime;
        
        if (diffInSeconds < 60) {
            formattedTime = 'agora mesmo';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            formattedTime = `${minutes} minuto${minutes > 1 ? 's' : ''} atrás`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            formattedTime = `${hours} hora${hours > 1 ? 's' : ''} atrás`;
        } else if (diffInSeconds < 2592000) { // 30 days
            const days = Math.floor(diffInSeconds / 86400);
            formattedTime = `${days} dia${days > 1 ? 's' : ''} atrás`;
        } else if (diffInSeconds < 31536000) { // 1 year
            const months = Math.floor(diffInSeconds / 2592000);
            formattedTime = `${months} mês${months > 1 ? 'es' : ''} atrás`;
        } else {
            const years = Math.floor(diffInSeconds / 31536000);
            formattedTime = `${years} ano${years > 1 ? 's' : ''} atrás`;
        }
        
        element.textContent = formattedTime;
    });
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @param {string} buttonId - ID of button to update
 */
function copyToClipboard(text, buttonId) {
    navigator.clipboard.writeText(text).then(() => {
        // Update button text
        const button = document.getElementById(buttonId);
        const originalText = button.textContent;
        button.textContent = 'Copiado!';
        
        // Reset button text after 2 seconds
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

/**
 * Show confirmation dialog
 * @param {string} message - Confirmation message
 * @param {function} callback - Function to call if confirmed
 */
function confirmAction(message, callback) {
    if (window.confirm(message)) {
        callback();
    }
}
