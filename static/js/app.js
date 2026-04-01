/**
 * THE PITCH VISUALIZER - Main JavaScript
 * Handles form submission, API calls, and UI updates
 */

// ============================================
// DOM Elements
// ============================================
const elements = {
    form: null,
    narrativeInput: null,
    styleSelect: null,
    generateBtn: null,
    loadingContainer: null,
    progressBar: null,
    progressStatus: null,
    storyboardSection: null,
    storyboardGrid: null,
    emptyState: null
};

// ============================================
// Initialize Application
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    attachEventListeners();
    console.log('🎨 Pitch Visualizer initialized');
});

/**
 * Cache DOM elements for performance
 */
function initializeElements() {
    elements.form = document.getElementById('generatorForm');
    elements.narrativeInput = document.getElementById('narrativeInput');
    elements.styleSelect = document.getElementById('styleSelect');
    elements.generateBtn = document.getElementById('generateBtn');
    elements.loadingContainer = document.getElementById('loadingContainer');
    elements.progressBar = document.getElementById('progressBar');
    elements.progressStatus = document.getElementById('progressStatus');
    elements.storyboardSection = document.getElementById('storyboardSection');
    elements.storyboardGrid = document.getElementById('storyboardGrid');
    elements.emptyState = document.getElementById('emptyState');
}

/**
 * Attach event listeners
 */
function attachEventListeners() {
    if (elements.form) {
        elements.form.addEventListener('submit', handleFormSubmit);
    }
    
    // Auto-resize textarea
    if (elements.narrativeInput) {
        elements.narrativeInput.addEventListener('input', autoResizeTextarea);
    }
}

// ============================================
// Form Handling
// ============================================

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const narrativeText = elements.narrativeInput.value.trim();
    const styleChoice = elements.styleSelect.value;
    
    // Validate input
    if (!narrativeText) {
        showNotification('Please enter a narrative text', 'error');
        elements.narrativeInput.focus();
        return;
    }
    
    if (narrativeText.length < 50) {
        showNotification('Please enter a more detailed narrative (at least 50 characters)', 'error');
        elements.narrativeInput.focus();
        return;
    }
    
    // Start generation process
    await generateStoryboard(narrativeText, styleChoice);
}

/**
 * Auto-resize textarea based on content
 */
function autoResizeTextarea() {
    const textarea = elements.narrativeInput;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 300) + 'px';
}

// ============================================
// API Communication
// ============================================

/**
 * Generate storyboard by calling the backend API
 */
async function generateStoryboard(text, style) {
    // Update UI to loading state
    setLoadingState(true);
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                style: style
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            renderStoryboard(data.storyboard);
            showNotification(`Successfully generated ${data.storyboard.length} slides!`, 'success');
        } else {
            throw new Error('Unexpected response from server');
        }
        
    } catch (error) {
        console.error('Generation error:', error);
        showNotification('Failed to generate storyboard. Please try again.', 'error');
        setLoadingState(false);
    }
}

// ============================================
// UI Rendering
// ============================================

/**
 * Set loading state
 */
function setLoadingState(isLoading) {
    if (isLoading) {
        elements.generateBtn.disabled = true;
        elements.generateBtn.innerHTML = `
            <span class="btn-icon">⏳</span>
            <span>Generating...</span>
        `;
        elements.loadingContainer.classList.add('active');
        elements.storyboardSection.classList.remove('active');
        
        // Start progress animation
        startProgressAnimation();
    } else {
        elements.generateBtn.disabled = false;
        elements.generateBtn.innerHTML = `
            <span class="btn-icon">✨</span>
            <span>Generate Storyboard</span>
        `;
        elements.loadingContainer.classList.remove('active');
        stopProgressAnimation();
    }
}

/**
 * Animate progress bar
 */
let progressInterval = null;

function startProgressAnimation() {
    let progress = 0;
    const stages = [
        { threshold: 20, text: '🧠 Analyzing narrative structure...' },
        { threshold: 40, text: '📝 Extracting story context...' },
        { threshold: 60, text: '🎨 Engineering visual prompts...' },
        { threshold: 80, text: '🖼️ Generating images (this takes ~30-60s)...' },
        { threshold: 100, text: '✨ Finalizing storyboard...' }
    ];
    
    progressInterval = setInterval(() => {
        progress += Math.random() * 5 + 2;
        
        if (progress >= 100) {
            progress = 95; // Cap at 95% until response arrives
        }
        
        elements.progressBar.style.width = progress + '%';
        
        // Update status text based on progress
        const currentStage = stages.slice().reverse().find(s => progress >= s.threshold);
        if (currentStage) {
            elements.progressStatus.textContent = currentStage.text;
        }
    }, 2000);
}

function stopProgressAnimation() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    elements.progressBar.style.width = '100%';
    elements.progressStatus.textContent = '✓ Complete!';
    
    // Reset after delay
    setTimeout(() => {
        elements.progressBar.style.width = '0%';
        elements.progressStatus.textContent = '';
    }, 2000);
}

/**
 * Render the storyboard grid
 */
function renderStoryboard(panels) {
    elements.storyboardGrid.innerHTML = '';
    
    panels.forEach((panel, index) => {
        const cardHTML = createStoryboardCard(panel, index);
        elements.storyboardGrid.insertAdjacentHTML('beforeend', cardHTML);
    });
    
    // Hide empty state and show storyboard section
    elements.emptyState.classList.add('hidden');
    elements.storyboardSection.classList.add('active');
    setLoadingState(false);
    
    // Scroll to results
    setTimeout(() => {
        elements.storyboardSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }, 100);
}

/**
 * Create a storyboard card HTML
 */
function createStoryboardCard(panel, index) {
    const emotionalToneLabels = {
        'stressed': '😰 Stressed',
        'overwhelmed': '😰 Overwhelmed',
        'curious': '🤔 Curious',
        'hopeful': '🌟 Hopeful',
        'focused': '🎯 Focused',
        'engaged': '💪 Engaged',
        'triumphant': '🏆 Triumphant',
        'successful': '✨ Successful',
        'neutral': '😐 Neutral'
    };
    
    const toneLabel = emotionalToneLabels[panel.emotional_tone?.toLowerCase()] || 
                      `😐 ${panel.emotional_tone || 'Neutral'}`;
    
    return `
        <article class="storyboard-card" style="animation-delay: ${index * 0.15}s">
            <!-- Card Header with Badges -->
            <div class="card-header">
                <div class="card-badges">
                    <span class="badge badge-scene">
                        📊 Slide ${panel.scene_number}
                    </span>
                    <span class="badge badge-label">
                        ${panel.scene_label || 'Scene'}
                    </span>
                </div>
                <span class="badge badge-tone">
                    ${toneLabel}
                </span>
            </div>
            
            <!-- Image Container (16:9 Aspect Ratio) -->
            <div class="card-image-container">
                <img 
                    src="${panel.image_url}" 
                    alt="${panel.scene_label || 'Scene ' + panel.scene_number}"
                    class="card-image"
                    loading="lazy"
                    onerror="this.src='https://via.placeholder.com/640x360?text=Image+Loading+Failed'"
                >
            </div>
            
            <!-- Card Content -->
            <div class="card-content">
                <!-- Scene Text (Quote) -->
                <blockquote class="card-text">
                    "${panel.text}"
                </blockquote>
                
                <!-- AI Prompt Box -->
                <div class="prompt-box">
                    <div class="prompt-label">
                        🤖 AI Engineered Prompt
                    </div>
                    <div class="prompt-text">${escapeHtml(panel.prompt)}</div>
                </div>
            </div>
        </article>
    `;
}

// ============================================
// Utility Functions
// ============================================

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification-toast');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification-toast notification-${type}`;
    notification.innerHTML = `
        <span class="notification-icon">${getNotificationIcon(type)}</span>
        <span class="notification-message">${message}</span>
    `;
    
    // Add styles
    Object.assign(notification.style, {
        position: 'fixed',
        bottom: '2rem',
        right: '2rem',
        padding: '1rem 1.5rem',
        background: type === 'success' ? 'linear-gradient(135deg, #10b981, #059669)' : 
                    type === 'error' ? 'linear-gradient(135deg, #ef4444, #dc2626)' :
                    'linear-gradient(135deg, #6366f1, #4f46e5)',
        color: 'white',
        borderRadius: '0.75rem',
        boxShadow: '0 10px 25px rgba(0,0,0,0.3)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        zIndex: '1000',
        animation: 'slideUp 0.3s ease',
        maxWidth: '400px'
    });
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideDown 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

/**
 * Get notification icon based on type
 */
function getNotificationIcon(type) {
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '⚠'
    };
    return icons[type] || icons.info;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Add animation keyframes dynamically
// ============================================
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideDown {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(20px);
        }
    }
`;
document.head.appendChild(style);
