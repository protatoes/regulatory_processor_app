/**
 * JavaScript for EU Regulatory Document Processor Frontend
 * Handles form submission, file upload, and real-time status updates
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const form = document.getElementById('processForm');
    const statusDiv = document.getElementById('status');
    const statusMessage = document.getElementById('statusMessage');
    const statusBadge = document.getElementById('statusBadge');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const fileList = document.getElementById('fileList');
    const errorList = document.getElementById('errorList');
    const results = document.getElementById('results');
    const submitBtn = document.getElementById('submitBtn');
    const submitText = document.getElementById('submitText');
    const submitSpinner = document.getElementById('submitSpinner');
    const folderPathInput = document.getElementById('folderPath');
    const mappingFileInput = document.getElementById('mappingFile');
    const fileInfo = document.getElementById('fileInfo');
    
    let currentTaskId = null;
    let statusInterval = null;
    
    // File input change handler
    mappingFileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            fileInfo.style.display = 'block';
            fileInfo.innerHTML = `
                <strong>Selected:</strong> ${file.name} 
                <span style="color: var(--gray-600);">(${formatFileSize(file.size)})</span>
            `;
        } else {
            fileInfo.style.display = 'none';
        }
    });
    
    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate inputs
        const folderPath = folderPathInput.value.trim();
        const mappingFile = mappingFileInput.files[0];
        
        if (!folderPath) {
            showError('Please enter a folder path');
            return;
        }
        
        if (!mappingFile) {
            showError('Please select a mapping file');
            return;
        }
        
        // Prepare form data
        const formData = new FormData();
        formData.append('folder_path', folderPath);
        formData.append('mapping_file', mappingFile);
        
        // Update UI to processing state
        setProcessingState(true);
        showStatus();
        updateStatus('started', 0, 'Starting processing...');
        
        try {
            // Submit processing request
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            currentTaskId = result.task_id;
            
            console.log('Processing started with task ID:', currentTaskId);
            
            // Start polling for status updates
            startStatusPolling();
            
        } catch (error) {
            console.error('Error starting processing:', error);
            updateStatus('error', 0, `Error: ${error.message}`);
            setProcessingState(false);
        }
    });
    
    /**
     * Start polling the server for status updates
     */
    function startStatusPolling() {
        if (statusInterval) {
            clearInterval(statusInterval);
        }
        
        statusInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/status/${currentTaskId}`);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                
                const status = await response.json();
                console.log('Status update:', status);
                
                updateStatus(status.status, status.progress, status.message);
                
                // Update results if available
                if (status.files && status.files.length > 0) {
                    showFiles(status.files);
                }
                
                if (status.errors && status.errors.length > 0) {
                    showErrors(status.errors);
                }
                
                // Stop polling if processing is complete
                if (['completed', 'failed', 'error'].includes(status.status)) {
                    clearInterval(statusInterval);
                    setProcessingState(false);
                    
                    if (status.status === 'completed') {
                        showSuccess('Processing completed successfully!');
                    }
                }
                
            } catch (error) {
                console.error('Status polling error:', error);
                // Don't stop polling on network errors, just log them
            }
        }, 1000); // Poll every second
    }
    
    /**
     * Update the status display
     */
    function updateStatus(status, progress, message) {
        // Update status badge
        statusBadge.className = `status-badge ${status}`;
        statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        
        // Update message
        statusMessage.textContent = message || status;
        
        // Update progress
        const progressValue = Math.max(0, Math.min(100, progress || 0));
        progressFill.style.width = `${progressValue}%`;
        progressText.textContent = `${progressValue}%`;
        
        // Show results section if we have files or errors
        if (status === 'completed' || status === 'failed') {
            results.style.display = 'block';
        }
    }
    
    /**
     * Show the status section
     */
    function showStatus() {
        statusDiv.style.display = 'block';
        results.style.display = 'none';
        fileList.innerHTML = '';
        errorList.innerHTML = '';
    }
    
    /**
     * Show generated files
     */
    function showFiles(files) {
        if (!files || files.length === 0) return;
        
        fileList.innerHTML = `
            <h4>✅ Generated Files (${files.length})</h4>
            ${files.map(file => `
                <div class="file-item">
                    📄 ${getFileName(file)}
                    <div style="font-size: 0.8rem; color: var(--gray-600); margin-top: 2px;">
                        ${file}
                    </div>
                </div>
            `).join('')}
        `;
    }
    
    /**
     * Show errors
     */
    function showErrors(errors) {
        if (!errors || errors.length === 0) return;
        
        errorList.innerHTML = `
            <h4>❌ Errors (${errors.length})</h4>
            ${errors.map(error => `
                <div class="error-item">
                    ⚠️ ${error}
                </div>
            `).join('')}
        `;
    }
    
    /**
     * Set processing state (enable/disable form)
     */
    function setProcessingState(isProcessing) {
        submitBtn.disabled = isProcessing;
        folderPathInput.disabled = isProcessing;
        mappingFileInput.disabled = isProcessing;
        
        if (isProcessing) {
            submitText.style.display = 'none';
            submitSpinner.style.display = 'block';
        } else {
            submitText.style.display = 'block';
            submitSpinner.style.display = 'none';
        }
    }
    
    /**
     * Show error message
     */
    function showError(message) {
        showStatus();
        updateStatus('error', 0, message);
        statusBadge.className = 'status-badge error';
        statusBadge.textContent = 'Error';
    }
    
    /**
     * Show success message
     */
    function showSuccess(message) {
        statusMessage.textContent = message;
        statusBadge.className = 'status-badge completed';
        statusBadge.textContent = 'Completed';
    }
    
    /**
     * Format file size for display
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    /**
     * Extract filename from full path
     */
    function getFileName(fullPath) {
        return fullPath.split('/').pop().split('\\').pop();
    }
    
    /**
     * Clean up on page unload
     */
    window.addEventListener('beforeunload', function() {
        if (statusInterval) {
            clearInterval(statusInterval);
        }
    });
    
    // Initialize form with some helpful defaults
    if (!folderPathInput.value) {
        // Set a helpful placeholder based on the user's OS
        const isWindows = navigator.platform.toLowerCase().includes('win');
        const isMac = navigator.platform.toLowerCase().includes('mac');
        
        if (isWindows) {
            folderPathInput.placeholder = 'C:\\Users\\username\\Documents\\smpc_files';
        } else if (isMac) {
            folderPathInput.placeholder = '/Users/username/Documents/smpc_files';
        } else {
            folderPathInput.placeholder = '/home/username/Documents/smpc_files';
        }
    }
    
    console.log('EU Regulatory Document Processor initialized');
});
