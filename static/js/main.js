/**
 * Premium Toast Notification System
 * @param {string} message - The message to display
 * @param {string} type - 'success', 'error', 'info', 'warning'
 * @param {number} duration - ms to show
 */
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';

    toast.innerHTML = `
        <i class="fas fa-${icon} toast-icon"></i>
        <div class="toast-content">${message}</div>
    `;

    // Click to hide early
    toast.onclick = () => hideToast(toast);

    container.appendChild(toast);

    // Auto-hide
    setTimeout(() => {
        hideToast(toast);
    }, duration);
}

function hideToast(toast) {
    if (toast.classList.contains('hiding')) return;
    toast.classList.add('hiding');
    setTimeout(() => {
        toast.remove();
    }, 300);
}

document.addEventListener('DOMContentLoaded', () => {
    const extractBtn = document.getElementById('extractBtn');
    const modal = document.getElementById('extractionModal');
    const closeModalBtn = document.querySelector('.close-modal');
    const processBtn = document.getElementById('processBtn');
    const rawText = document.getElementById('rawText');
    const resultsArea = document.getElementById('extractionResults');
    const jsonOutput = document.getElementById('jsonOutput');

    // Guard: extraction modal may not exist on every page
    if (!extractBtn || !modal) return;

    // Show extraction modal — use 'flex' (not 'block') so CSS centering works
    extractBtn.addEventListener('click', () => {
        modal.style.display = 'flex';
    });

    // Close modal button
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => {
            modal.style.display = 'none';
            resultsArea.classList.add('hidden');
            rawText.value = '';
        });
    }

    // Handle NLP extraction
    processBtn.addEventListener('click', async () => {
        const text = rawText.value.trim();
        if (!text) {
            showToast('Please paste some text first.', 'warning');
            return;
        }

        processBtn.disabled = true;
        processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

        try {
            // Read CSRF token from meta tag added in base.html
            const csrfMeta = document.querySelector('meta[name="csrf-token"]');
            const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : '';

            const response = await fetch('/process-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ text })
            });

            const result = await response.json();

            if (result.success) {
                resultsArea.classList.remove('hidden');
                jsonOutput.textContent = result.extracted;
                showToast('Data extracted successfully!', 'success');
            } else {
                showToast('Error: ' + (result.error || result.message || 'Unknown error'), 'error');
            }
        } catch (error) {
            console.error('Extraction Error:', error);
            showToast('Something went wrong. Please check the console.', 'error');
        } finally {
            processBtn.disabled = false;
            processBtn.innerHTML = 'Process with Qwen';
        }
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
            resultsArea.classList.add('hidden');
        }
    });
});
