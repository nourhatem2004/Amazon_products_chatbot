// Global variables
let isTyping = false;
let messageCount = 0;

// DOM elements
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const typingIndicator = document.getElementById('typingIndicator');
const loadingOverlay = document.getElementById('loadingOverlay');

// Initialize the chat
document.addEventListener('DOMContentLoaded', function() {
    messageInput.focus();
    
    // Event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-resize input
    messageInput.addEventListener('input', function() {
        updateSendButtonState();
    });
    
    updateSendButtonState();
});

// Update send button state
function updateSendButtonState() {
    const hasText = messageInput.value.trim().length > 0;
    sendButton.disabled = !hasText || isTyping;
    
    if (hasText && !isTyping) {
        sendButton.style.background = 'linear-gradient(135deg, #4f46e5, #7c3aed)';
    } else {
        sendButton.style.background = 'linear-gradient(135deg, #9ca3af, #6b7280)';
    }
}

// Send message function
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isTyping) return;
    
    // Add user message to chat
    addMessage(message, true);
    
    // Clear input
    messageInput.value = '';
    updateSendButtonState();
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send request to backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        if (data.status === 'success') {
            // Add bot response with fade animation
            addBotMessageWithFade(data.response);
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', false);
        }
    } catch (error) {
        console.error('Error:', error);
        hideTypingIndicator();
        addMessage('Sorry, I couldn\'t process your request. Please check your connection and try again.', false);
    }
}

// Add message to chat
function addMessage(text, isUser) {
    messageCount++;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px) scale(0.95)';
    messageDiv.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
    
    const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${isUser ? 'fa-user' : 'fa-robot'}"></i>
        </div>
        <div class="message-content">
            <div class="message-bubble">
                <p>${formatMessage(text)}</p>
            </div>
            <span class="message-time">${currentTime}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Animate message appearance
    setTimeout(() => {
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0) scale(1)';
    }, 50);
    
    scrollToBottom();
}

// Add bot message with fade-in effect
function addBotMessageWithFade(text) {
    messageCount++;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px) scale(0.95)';
    messageDiv.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
    
    const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-bubble">
                <p>${formatMessage(text)}</p>
            </div>
            <span class="message-time">${currentTime}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Animate message appearance with bounce effect
    setTimeout(() => {
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0) scale(1)';
    }, 100);
    
    // Add a subtle pulse effect to the avatar
    const avatar = messageDiv.querySelector('.message-avatar');
    setTimeout(() => {
        avatar.style.animation = 'avatarPulse 0.6s ease-out';
    }, 200);
    
    scrollToBottom();
}

// Format message text
function formatMessage(text) {
    // Convert markdown-like formatting
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert URLs to links
    text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Show typing indicator
function showTypingIndicator() {
    isTyping = true;
    typingIndicator.style.display = 'flex';
    updateSendButtonState();
    scrollToBottom();
}

// Hide typing indicator
function hideTypingIndicator() {
    isTyping = false;
    typingIndicator.style.display = 'none';
    updateSendButtonState();
}

// Scroll to bottom of chat
function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

// Send suggestion
function sendSuggestion(suggestion) {
    messageInput.value = suggestion;
    updateSendButtonState();
    sendMessage();
}

// Show loading overlay
function showLoading() {
    loadingOverlay.style.display = 'flex';
}

// Hide loading overlay
function hideLoading() {
    loadingOverlay.style.display = 'none';
}

// Handle window resize
window.addEventListener('resize', () => {
    scrollToBottom();
});

// Handle focus on input when clicking anywhere in input area
document.querySelector('.input-container').addEventListener('click', () => {
    messageInput.focus();
});
