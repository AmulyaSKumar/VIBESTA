document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabId = this.getAttribute('data-tab');
                
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.add('hidden');
                });
                
                // Show the selected tab content
                document.getElementById(tabId).classList.remove('hidden');
                
                // Update active class for tab buttons
                tabButtons.forEach(btn => {
                    btn.classList.remove('active');
                });
                this.classList.add('active');
            });
        });
    }

    // Drag and drop file upload
    const dragDropArea = document.querySelector('.drag-drop-area');
    const fileInput = document.getElementById('file');
    const previewContainer = document.querySelector('.preview-container');
    const dragDropPrompt = document.querySelector('.drag-drop-prompt');
    const previewImage = document.querySelector('.preview-image');
    const previewVideo = document.querySelector('.preview-video');
    const fileName = document.querySelector('.file-name');
    const browseButton = document.querySelector('.browse-button');
    const removeFileBtn = document.querySelector('.remove-file-btn');

    if (dragDropArea && fileInput) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dragDropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Highlight drop area when item is dragged over
        ['dragenter', 'dragover'].forEach(eventName => {
            dragDropArea.addEventListener(eventName, highlight, false);
        });
        
        // Remove highlight when item is dragged away
        ['dragleave', 'drop'].forEach(eventName => {
            dragDropArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dragDropArea.classList.add('highlight');
        }
        
        function unhighlight() {
            dragDropArea.classList.remove('highlight');
        }
        
        // Handle dropped files
        dragDropArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length) {
                fileInput.files = files;
                handleFiles(files);
            }
        }
        
        // Browse button functionality
        if (browseButton) {
            browseButton.addEventListener('click', function() {
                fileInput.click();
            });
        }
        
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length) {
                handleFiles(fileInput.files);
            }
        });
        
        function handleFiles(files) {
            const file = files[0];
            
            if (file) {
                showPreview(file);
            }
        }
        
        function showPreview(file) {
            const fileType = file.type.split('/')[0];
            
            // Show file name
            fileName.textContent = file.name;
            
            // Create URL for preview
            const fileURL = URL.createObjectURL(file);
            
            // Hide prompt, show preview
            dragDropPrompt.style.display = 'none';
            previewContainer.style.display = 'flex';
            
            // Show appropriate preview based on file type
            if (fileType === 'image') {
                previewImage.src = fileURL;
                previewImage.style.display = 'block';
                previewVideo.style.display = 'none';
            } else if (fileType === 'video') {
                previewVideo.src = fileURL;
                previewVideo.style.display = 'block';
                previewImage.style.display = 'none';
            }
        }
        
        // Remove file button functionality
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', function() {
                // Clear file input
                fileInput.value = '';
                
                // Hide preview, show prompt
                previewContainer.style.display = 'none';
                dragDropPrompt.style.display = 'flex';
                
                // Clear preview sources
                previewImage.src = '';
                previewVideo.src = '';
                fileName.textContent = '';
            });
        }
    }

    // Character counter for textarea
    const storyTextarea = document.getElementById('caption');
    const charCounter = document.querySelector('.char-counter');
    
    if (storyTextarea && charCounter) {
        storyTextarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            charCounter.textContent = `${currentLength} / 500 characters`;
            
            if (currentLength > 500) {
                charCounter.style.color = '#e74c3c';
            } else {
                charCounter.style.color = '#7f8c8d';
            }
        });
    }

    // Flash message auto-hide
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.style.display = 'none';
                }, 500);
            }, 5000);
        });
    }

    // Copy post link functionality
    const copyLinkButtons = document.querySelectorAll('.copy-link-button');
    const copyToast = document.getElementById('copy-toast');
    
    if (copyLinkButtons.length > 0) {
        copyLinkButtons.forEach(button => {
            button.addEventListener('click', function() {
                const postUrl = this.getAttribute('data-url') || window.location.href;
                
                // Copy to clipboard
                navigator.clipboard.writeText(postUrl).then(() => {
                    // Show toast
                    if (copyToast) {
                        copyToast.classList.add('show');
                        setTimeout(() => {
                            copyToast.classList.remove('show');
                        }, 3000);
                    }
                }).catch(err => {
                    console.error('Could not copy text: ', err);
                });
            });
        });
    }

    // Social media sharing
    const shareButtons = document.querySelectorAll('[data-share]');
    
    if (shareButtons.length > 0) {
        shareButtons.forEach(button => {
            button.addEventListener('click', function() {
                const platform = this.getAttribute('data-share');
                const url = this.getAttribute('data-url') || window.location.href;
                const title = this.getAttribute('data-title') || document.title;
                let shareUrl;
                
                switch(platform) {
                    case 'facebook':
                        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
                        break;
                    case 'twitter':
                        shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;
                        break;
                    case 'whatsapp':
                        shareUrl = `https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}`;
                        break;
                }
                
                if (shareUrl) {
                    window.open(shareUrl, '_blank', 'width=600,height=400');
                }
            });
        });
    }
}); 