let currentConversationId = null;
let messages = [];
let isSidebarOpen = window.innerWidth > 768;

document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    setupEventListeners();
    updateSidebarState();
    
    // Create overlay for mobile
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.addEventListener('click', toggleChatSidebar);
    document.querySelector('.chat-layout').appendChild(overlay);
});

function initializeChat() {
    // Load initial conversation if any
    const activeConversation = document.querySelector('.conversation-item.active');
    if (activeConversation) {
        currentConversationId = activeConversation.dataset.conversationId;
    }
}

function setupEventListeners() {
    // Chat form submission
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleSendMessage);
    }

    // Auto-resize textarea
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        // Enter to send (Shift+Enter for new line)
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (chatForm) {
                    chatForm.dispatchEvent(new Event('submit'));
                }
            }
        });
    }

    // Toggle chat sidebar button
    const toggleBtn = document.getElementById('toggle-chat-sidebar-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleChatSidebar);
    }

    // New conversation button
    const newConvBtn = document.getElementById('new-conversation-btn');
    if (newConvBtn) {
        newConvBtn.addEventListener('click', startNewConversation);
    }

    // Clear chat button
    const clearBtn = document.getElementById('clear-chat-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearChat);
    }

    // Export chat button
    const exportBtn = document.getElementById('export-chat-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportChat);
    }

    // Settings button
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', showSettings);
    }

    // Conversation delete buttons
    document.querySelectorAll('.conversation-delete-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const conversationItem = this.closest('.conversation-item');
            if (conversationItem) {
                deleteConversation(conversationItem.dataset.conversationId);
            }
        });
    });

    // Conversation click handlers
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.addEventListener('click', function() {
            const conversationId = this.dataset.conversationId;
            if (conversationId) {
                loadConversation(conversationId);
                if (window.innerWidth <= 768) {
                    toggleChatSidebar();
                }
            }
        });
    });

    // Window resize handler
    window.addEventListener('resize', handleResize);
}

function toggleChatSidebar() {
    const sidebar = document.getElementById('chat-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (sidebar) {
        isSidebarOpen = !isSidebarOpen;
        sidebar.classList.toggle('open', isSidebarOpen);
        
        if (window.innerWidth <= 768) {
            if (overlay) {
                overlay.classList.toggle('active', isSidebarOpen);
            }
        }
        
        updateSidebarState();
    }
}

function handleResize() {
    const overlay = document.querySelector('.sidebar-overlay');
    if (window.innerWidth > 768) {
        if (overlay) {
            overlay.classList.remove('active');
        }
        isSidebarOpen = true;
        const sidebar = document.getElementById('chat-sidebar');
        if (sidebar) {
            sidebar.classList.add('open');
        }
    } else {
        isSidebarOpen = false;
        const sidebar = document.getElementById('chat-sidebar');
        if (sidebar) {
            sidebar.classList.remove('open');
        }
    }
}

function handleSendMessage(e) {
    e.preventDefault();
    
    const input = document.getElementById('chat-input');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;

    // Add user message to UI
    addMessageToUI(message, 'user');
    
    // Clear input and reset height
    input.value = '';
    input.style.height = 'auto';

    // Show typing indicator
    showTypingIndicator();

    // Simulate AI response
    setTimeout(() => {
        hideTypingIndicator();
        const aiResponse = generateAIResponse(message);
        addMessageToUI(aiResponse, 'ai');
    }, 1000 + Math.random() * 1000);
}

function addMessageToUI(text, sender) {
    const messagesArea = document.getElementById('chat-messages');
    if (!messagesArea) return;

    // Remove welcome screen if present
    const welcomeScreen = document.getElementById('welcome-screen');
    if (welcomeScreen && sender === 'user') {
        welcomeScreen.style.display = 'none';
    }

    const messageHTML = `
        <div class="message ${sender}">
            <div class="message-avatar">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${escapeHtml(text)}</div>
                <div class="message-time">${formatTime(new Date())}</div>
            </div>
        </div>
    `;
    
    messagesArea.insertAdjacentHTML('beforeend', messageHTML);
    scrollToBottom();
}

function showTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.style.display = 'flex';
        scrollToBottom();
    }
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

function generateAIResponse(message) {
    const responses = {
        'project': "I'd be happy to help you plan your project! Let's start by defining the main objectives and breaking them down into manageable tasks. What's the primary goal of your project?",
        'productivity': "Improving productivity starts with effective time management. Consider using techniques like time blocking, the Pomodoro method, and prioritizing tasks based on importance and urgency.",
        'tasks': "For better task organization, I recommend categorizing tasks by priority and deadline. Tools like Kanban boards or task management apps can help visualize your workflow.",
        'team': "Effective team management involves clear communication, regular check-ins, and defined roles. For remote teams, establish consistent meeting rhythms and use collaborative tools.",
        'default': "That's an interesting question! I'd be happy to help you with that. Could you provide a bit more context so I can give you the most relevant advice?"
    };

    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('project') || lowerMessage.includes('plan')) {
        return responses.project;
    } else if (lowerMessage.includes('productivity') || lowerMessage.includes('efficient')) {
        return responses.productivity;
    } else if (lowerMessage.includes('task') || lowerMessage.includes('organize')) {
        return responses.tasks;
    } else if (lowerMessage.includes('team') || lowerMessage.includes('manage')) {
        return responses.team;
    } else {
        return responses.default;
    }
}

function sendQuickMessage(message) {
    const input = document.getElementById('chat-input');
    if (input) {
        input.value = message;
        const event = new Event('submit', { cancelable: true });
        const form = document.getElementById('chat-form');
        if (form) {
            form.dispatchEvent(event);
        }
    }
}

function startNewConversation() {
    showToast('Starting new conversation...');
    
    // Clear current messages
    messages = [];
    const messagesArea = document.getElementById('chat-messages');
    const welcomeScreen = document.getElementById('welcome-screen');
    
    if (messagesArea) {
        if (welcomeScreen) {
            welcomeScreen.style.display = 'flex';
        } else {
            messagesArea.innerHTML = `
                <div class="welcome-screen" id="welcome-screen">
                    <div class="welcome-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h3>New Conversation Started</h3>
                    <p>What would you like to discuss?</p>
                    <div class="quick-suggestions">
                        <!-- Quick suggestions would be recreated here -->
                    </div>
                </div>
            `;
        }
    }
    
    // Update active conversation
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    
    currentConversationId = null;
    scrollToBottom();
}

function loadConversation(conversationId) {
    showToast(`Loading conversation...`);
    currentConversationId = conversationId;
    
    // Update active state
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const targetConversation = document.querySelector(`[data-conversation-id="${conversationId}"]`);
    if (targetConversation) {
        targetConversation.classList.add('active');
    }
    
    // Simulate loading messages
    setTimeout(() => {
        const messagesArea = document.getElementById('chat-messages');
        if (messagesArea) {
            messagesArea.innerHTML = `
                <div class="message ai">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-text">Welcome back to this conversation! How can I continue assisting you?</div>
                        <div class="message-time">${formatTime(new Date())}</div>
                    </div>
                </div>
            `;
            scrollToBottom();
        }
    }, 500);
}

function deleteConversation(conversationId) {
    if (confirm('Are you sure you want to delete this conversation?')) {
        const conversationItem = document.querySelector(`[data-conversation-id="${conversationId}"]`);
        if (conversationItem) {
            conversationItem.style.opacity = '0';
            conversationItem.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                conversationItem.remove();
                showToast('Conversation deleted');
                
                // If deleted conversation was active, start new one
                if (currentConversationId === conversationId) {
                    startNewConversation();
                }
            }, 300);
        }
    }
}

function clearChat() {
    if (confirm('Are you sure you want to clear this chat?')) {
        const messagesArea = document.getElementById('chat-messages');
        if (messagesArea) {
            messagesArea.innerHTML = '';
            messages = [];
            showToast('Chat cleared');
        }
    }
}

function exportChat() {
    showToast('Exporting chat...');
    // In a real application, this would generate and download a file
    setTimeout(() => {
        showToast('Chat exported successfully!');
    }, 1000);
}

function showSettings() {
    showToast('Opening settings...');
    // In a real application, this would open a settings modal
}

function scrollToBottom() {
    const messagesArea = document.getElementById('chat-messages');
    if (messagesArea) {
        setTimeout(() => {
            messagesArea.scrollTop = messagesArea.scrollHeight;
        }, 100);
    }
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true
    });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message) {
    const toast = document.getElementById('toast');
    if (toast) {
        toast.textContent = message;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}