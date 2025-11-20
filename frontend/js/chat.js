let currentConversationId = 1;
let messages = [];
let isSidebarOpen = window.innerWidth > 768;

document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    setupEventListeners();
    updateSidebarVisibility();
});

function initializeChat() {
    const activeConversation = document.querySelector('.conversation-item.active');
    if (activeConversation) {
        currentConversationId = activeConversation.dataset.conversationId;
    }
}

function setupEventListeners() {
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleSendMessage);
    }

    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });
    }

    const toggleBtn = document.getElementById('toggle-sidebar-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleSidebar);
    }

    const overlay = document.getElementById('sidebar-overlay');
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    const newConvBtn = document.getElementById('new-conversation-btn');
    if (newConvBtn) {
        newConvBtn.addEventListener('click', startNewConversation);
    }

    const clearBtn = document.getElementById('clear-chat-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearChat);
    }

    const exportBtn = document.getElementById('export-chat-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportChat);
    }

    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', showSettings);
    }

    document.querySelectorAll('.conversation-item').forEach(item => {
        item.addEventListener('click', function() {
            const conversationId = this.dataset.conversationId;
            if (conversationId) {
                loadConversation(conversationId);
            }
        });
    });

    document.querySelectorAll('.conversation-delete-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const conversationItem = this.closest('.conversation-item');
            if (conversationItem) {
                deleteConversation(conversationItem.dataset.conversationId);
            }
        });
    });

    window.addEventListener('resize', handleResize);
}

function toggleSidebar() {
    const sidebar = document.getElementById('chat-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    isSidebarOpen = !isSidebarOpen;
    
    if (sidebar) {
        sidebar.classList.toggle('open', isSidebarOpen);
    }
    
    if (overlay && window.innerWidth <= 768) {
        overlay.classList.toggle('active', isSidebarOpen);
    }
}

function closeSidebar() {
    const sidebar = document.getElementById('chat-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    isSidebarOpen = false;
    
    if (sidebar) {
        sidebar.classList.remove('open');
    }
    
    if (overlay) {
        overlay.classList.remove('active');
    }
}

function updateSidebarVisibility() {
    const sidebar = document.getElementById('chat-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (window.innerWidth > 768) {
        isSidebarOpen = true;
        if (sidebar) {
            sidebar.classList.add('open');
        }
        if (overlay) {
            overlay.classList.remove('active');
        }
    } else {
        isSidebarOpen = false;
        if (sidebar) {
            sidebar.classList.remove('open');
        }
        if (overlay) {
            overlay.classList.remove('active');
        }
    }
}

function handleResize() {
    updateSidebarVisibility();
}

function handleSendMessage(e) {
    if (e) e.preventDefault();
    
    const input = document.getElementById('chat-input');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;

    addMessageToUI(message, 'user');
    
    input.value = '';
    input.style.height = 'auto';

    showTypingIndicator();

    setTimeout(() => {
        hideTypingIndicator();
        const aiResponse = generateAIResponse(message);
        addMessageToUI(aiResponse, 'ai');
    }, 1000 + Math.random() * 1000);

    if (window.innerWidth <= 768) {
        closeSidebar();
    }
}

function addMessageToUI(text, sender) {
    const messagesArea = document.getElementById('chat-messages');
    if (!messagesArea) return;

    const welcomeScreen = document.getElementById('welcome-screen');
    if (welcomeScreen && sender === 'user') {
        welcomeScreen.style.display = 'none';
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = `<i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const textDiv = document.createElement('div');
    textDiv.className = 'message-text';
    textDiv.textContent = text;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = formatTime(new Date());
    
    contentDiv.appendChild(textDiv);
    contentDiv.appendChild(timeDiv);
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    messagesArea.appendChild(messageDiv);
    scrollToBottom();
    
    messages.push({ text, sender, timestamp: new Date() });
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
        handleSendMessage();
    }
}

function startNewConversation() {
    if (messages.length > 0 && !confirm('Start a new conversation? Current chat will be saved.')) {
        return;
    }

    showToast('Starting new conversation...');
    
    messages = [];
    const messagesArea = document.getElementById('chat-messages');
    
    if (messagesArea) {
        messagesArea.innerHTML = `
            <div class="welcome-screen" id="welcome-screen">
                <div class="welcome-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <h3>New Conversation Started</h3>
                <p>What would you like to discuss today?</p>
                <div class="quick-suggestions">
                    <button class="suggestion-card" onclick="sendQuickMessage('Help me plan a new project')">
                        <div class="suggestion-icon" style="background: linear-gradient(135deg, #06b6d4, #ec4899);">
                            <i class="fas fa-project-diagram"></i>
                        </div>
                        <h4>Project Planning</h4>
                        <p>Get help planning your next project</p>
                    </button>
                    <button class="suggestion-card" onclick="sendQuickMessage('How can I improve my productivity?')">
                        <div class="suggestion-icon" style="background: linear-gradient(135deg, #8b5cf6, #ec4899);">
                            <i class="fas fa-bolt"></i>
                        </div>
                        <h4>Productivity Tips</h4>
                        <p>Learn ways to be more productive</p>
                    </button>
                    <button class="suggestion-card" onclick="sendQuickMessage('Help me organize my tasks')">
                        <div class="suggestion-icon" style="background: linear-gradient(135deg, #10b981, #06b6d4);">
                            <i class="fas fa-tasks"></i>
                        </div>
                        <h4>Task Organization</h4>
                        <p>Get help organizing your tasks</p>
                    </button>
                    <button class="suggestion-card" onclick="sendQuickMessage('What are the best team management practices?')">
                        <div class="suggestion-icon" style="background: linear-gradient(135deg, #f97316, #ef4444);">
                            <i class="fas fa-users-cog"></i>
                        </div>
                        <h4>Team Management</h4>
                        <p>Learn team management best practices</p>
                    </button>
                </div>
            </div>
        `;
    }
    
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    
    currentConversationId = null;
    scrollToBottom();
}

function loadConversation(conversationId) {
    showToast('Loading conversation...');
    currentConversationId = conversationId;
    
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const targetConversation = document.querySelector(`[data-conversation-id="${conversationId}"]`);
    if (targetConversation) {
        targetConversation.classList.add('active');
    }
    
    setTimeout(() => {
        const messagesArea = document.getElementById('chat-messages');
        if (messagesArea) {
            messagesArea.innerHTML = `
                <div class="message ai">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-text">Welcome back! I've loaded your previous conversation. How can I continue assisting you?</div>
                        <div class="message-time">${formatTime(new Date())}</div>
                    </div>
                </div>
            `;
            scrollToBottom();
        }
    }, 500);

    if (window.innerWidth <= 768) {
        closeSidebar();
    }
}

function deleteConversation(conversationId) {
    if (!confirm('Are you sure you want to delete this conversation?')) {
        return;
    }

    const conversationItem = document.querySelector(`[data-conversation-id="${conversationId}"]`);
    if (conversationItem) {
        conversationItem.style.opacity = '0';
        conversationItem.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            conversationItem.remove();
            showToast('Conversation deleted');
            
            if (currentConversationId == conversationId) {
                startNewConversation();
            }
        }, 300);
    }
}

function clearChat() {
    if (messages.length === 0) {
        showToast('Chat is already empty');
        return;
    }

    if (!confirm('Are you sure you want to clear this chat?')) {
        return;
    }

    const messagesArea = document.getElementById('chat-messages');
    const welcomeScreen = document.getElementById('welcome-screen');
    
    if (messagesArea) {
        if (welcomeScreen) {
            welcomeScreen.style.display = 'flex';
            const allMessages = messagesArea.querySelectorAll('.message');
            allMessages.forEach(msg => msg.remove());
        } else {
            messagesArea.innerHTML = `
                <div class="welcome-screen" id="welcome-screen">
                    <div class="welcome-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h3>Chat Cleared</h3>
                    <p>Ready to start fresh! What would you like to discuss?</p>
                </div>
            `;
        }
        
        messages = [];
        showToast('Chat cleared');
        scrollToBottom();
    }
}

function exportChat() {
    if (messages.length === 0) {
        showToast('No messages to export');
        return;
    }

    showToast('Exporting chat...');
    
    setTimeout(() => {
        let exportText = 'Loop AI Chat Export\n';
        exportText += '===================\n\n';
        
        messages.forEach(msg => {
            const time = formatTime(msg.timestamp);
            exportText += `[${time}] ${msg.sender.toUpperCase()}: ${msg.text}\n\n`;
        });
        
        const blob = new Blob([exportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `loop-ai-chat-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('Chat exported successfully!');
    }, 500);
}

function showSettings() {
    showToast('Settings feature coming soon!');
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

window.sendQuickMessage = sendQuickMessage;