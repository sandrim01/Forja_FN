/**
 * Forja FN - Payment Processing
 * Handles PIX payment processing and status checking
 */

document.addEventListener('DOMContentLoaded', function() {
    const pixPayment = document.getElementById('pixPayment');
    if (pixPayment) {
        initializePaymentMonitoring();
    }
});

/**
 * Initialize the payment status monitoring
 */
function initializePaymentMonitoring() {
    const paymentId = document.getElementById('paymentId').value;
    
    if (paymentId) {
        // Check payment status every 10 seconds
        checkPaymentStatus(paymentId);
        setInterval(() => checkPaymentStatus(paymentId), 10000);
        
        // Setup copy buttons
        setupCopyButtons();
    }
}

/**
 * Check the current payment status
 * @param {string} paymentId - The payment ID to check
 */
function checkPaymentStatus(paymentId) {
    // In a real application, this would make an API call to check payment status
    // For demo purposes, we'll simulate a successful payment after 30 seconds
    
    const paymentStartTime = localStorage.getItem(`payment_${paymentId}_start`);
    
    if (!paymentStartTime) {
        localStorage.setItem(`payment_${paymentId}_start`, Date.now());
    } else {
        const elapsed = (Date.now() - parseInt(paymentStartTime)) / 1000;
        
        // Simulate payment completion after 30 seconds
        if (elapsed > 30) {
            // Redirect to success page
            window.location.href = `/payment/success/${paymentId}`;
        }
    }
}

/**
 * Setup copy buttons for PIX code
 */
function setupCopyButtons() {
    // Copy PIX code
    const copyCodeBtn = document.getElementById('copyPIXCode');
    if (copyCodeBtn) {
        const pixCode = document.getElementById('pixCode').textContent;
        
        copyCodeBtn.addEventListener('click', function() {
            copyToClipboard(pixCode, 'copyPIXCode');
        });
    }
}

/**
 * Manually complete payment (for demo purposes)
 */
function completePayment() {
    const paymentId = document.getElementById('paymentId').value;
    window.location.href = `/payment/success/${paymentId}`;
}
