let currentConversationId = 1;
let messages = [];
let isSidebarOpen = window.innerWidth > 768;

document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    setupEventListeners();
    updateSidebarVisibility();
    populateUserProfile();
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

async function populateUserProfile() {
    try {
        const nameEl = document.querySelector('.user-profile .user-name');
        const initialEl = document.querySelector('.user-profile .avatar-initial');
        const statusEl = document.querySelector('.user-profile .user-status');
        if (!nameEl || !initialEl || !statusEl) return;

        const user = await window.API.users.getProfile();
        const displayName = (user.first_name || user.last_name)
            ? `${user.first_name || ''} ${user.last_name || ''}`.trim()
            : (user.username || user.email || 'You');

        nameEl.textContent = displayName;
        initialEl.textContent = (displayName || 'U').trim().charAt(0).toUpperCase();
        statusEl.textContent = 'Online';
        statusEl.classList.remove('offline');
        statusEl.classList.add('online');
    } catch (e) {
        // Fallback for anonymous/no token
        const nameEl = document.querySelector('.user-profile .user-name');
        const initialEl = document.querySelector('.user-profile .avatar-initial');
        const statusEl = document.querySelector('.user-profile .user-status');
        if (nameEl && !nameEl.textContent) nameEl.textContent = 'Guest';
        if (initialEl && !initialEl.textContent) initialEl.textContent = 'G';
        if (statusEl) {
            statusEl.textContent = 'Offline';
            statusEl.classList.remove('online');
            statusEl.classList.add('offline');
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
    const lowerMessage = message.toLowerCase();
    
    // Greeting responses
    if (lowerMessage.match(/^(hi|hello|hey|greetings|good morning|good afternoon|good evening)/i)) {
        const greetings = [
            "👋 Hello! I'm S T manger, your personal task management assistant. How can I help you today?",
            "Hey there! Ready to boost your productivity? What would you like to work on?",
            "Greetings! I'm here to help with task management, projects, and productivity. What's on your mind?"
        ];
        return greetings[Math.floor(Math.random() * greetings.length)];
    }

    // Project Planning
    if (lowerMessage.includes('project') || lowerMessage.includes('plan') || lowerMessage.includes('planning')) {
        const projectResponses = [
            "🎯 Great! Project planning is key to success. Here's my approach:\n\n1. **Define Goals** - What's the end result?\n2. **Identify Tasks** - Break it into actionable steps\n3. **Set Timeline** - Realistic deadlines\n4. **Assign Resources** - Who's doing what?\n5. **Track Progress** - Regular check-ins\n\nWhat type of project are you planning?",
            "📋 For effective project planning, I recommend:\n- Start with a clear vision and objectives\n- Use the SMART method (Specific, Measurable, Achievable, Relevant, Time-bound)\n- Create a project roadmap with milestones\n- Break down into smaller sprints\n- Define dependencies between tasks\n\nWould you like help with any specific aspect?",
            "🚀 Project planning checklist:\n✓ Define scope and objectives\n✓ Identify stakeholders\n✓ Create timeline and milestones\n✓ Allocate resources and budget\n✓ Establish communication plan\n✓ Plan for risks\n\nTell me more about your project!"
        ];
        return projectResponses[Math.floor(Math.random() * projectResponses.length)];
    }

    // Productivity & Efficiency
    if (lowerMessage.includes('productivity') || lowerMessage.includes('efficient') || lowerMessage.includes('improve') || lowerMessage.includes('better')) {
        const productivityResponses = [
            "⚡ Here are proven productivity boosters:\n\n**Time Management Techniques:**\n- 🍅 Pomodoro: 25-min focused work + 5-min break\n- 🎯 Time Blocking: Schedule specific tasks\n- 📊 Eisenhower Matrix: Prioritize by importance\n\n**Daily Habits:**\n- Start with your hardest task\n- Minimize distractions (notifications off)\n- Take regular breaks\n- Track what you accomplish\n\nWhich technique interests you most?",
            "💪 Productivity tips:\n1. **Energy Management** - Work during peak hours\n2. **Deep Work** - 90-120 min uninterrupted focus\n3. **Task Batching** - Group similar tasks\n4. **Say No** - Protect your time\n5. **Review & Optimize** - Weekly reflection\n\nWhat's your biggest productivity challenge?",
            "🎪 To maximize productivity:\n✓ Eliminate context switching\n✓ Use the \"Eat the Frog\" method (hard tasks first)\n✓ Keep a clear desk\n✓ Turn off notifications\n✓ Celebrate small wins\n✓ Review daily\n\nWhat would help you most right now?"
        ];
        return productivityResponses[Math.floor(Math.random() * productivityResponses.length)];
    }

    // Task Organization
    if (lowerMessage.includes('task') || lowerMessage.includes('organize') || lowerMessage.includes('todo') || lowerMessage.includes('schedule')) {
        const taskResponses = [
            "📝 Task organization system:\n\n**Step 1: Capture** - Write down ALL tasks\n**Step 2: Clarify** - Is it actionable?\n**Step 3: Organize** - By context or priority\n**Step 4: Reflect** - Weekly review\n**Step 5: Engage** - Take action\n\n**Priority Levels:**\n🔴 High - Do today\n🟡 Medium - This week\n🟢 Low - When you have time\n\nLet's organize your tasks!",
            "🎯 Task management best practices:\n- Create a single source of truth\n- Use categories (Work, Personal, etc)\n- Set realistic deadlines\n- Break big tasks into subtasks\n- Review daily (5 min)\n- Use colors/labels for quick scanning\n\nHow many tasks are you juggling right now?",
            "✅ My recommended approach:\n1. **Inbox Zero** - Capture all ideas\n2. **Weekly Review** - Every Friday\n3. **Daily Planning** - Top 3 priorities\n4. **Quick Wins** - Build momentum\n5. **Context Switching** - Batch similar tasks\n\nWhat task are you struggling with?"
        ];
        return taskResponses[Math.floor(Math.random() * taskResponses.length)];
    }

    // Team & Collaboration
    if (lowerMessage.includes('team') || lowerMessage.includes('manage') || lowerMessage.includes('collaborate') || lowerMessage.includes('communication')) {
        const teamResponses = [
            "👥 Effective team management:\n\n**Communication:**\n- Daily standups (15 min)\n- Weekly planning\n- Clear async communication\n- Documented decisions\n\n**Process:**\n- Defined roles & responsibilities\n- Clear project goals\n- Regular 1-on-1s\n- Constructive feedback\n\n**Tools:**\n- Project management system\n- Chat for quick updates\n- Documentation hub\n\nWhat's your team size?",
            "🤝 Team collaboration tips:\n✓ Set clear expectations\n✓ Celebrate wins together\n✓ Address conflicts early\n✓ Foster psychological safety\n✓ Remote-friendly meetings\n✓ Async-first communication\n\nAny team challenges to discuss?",
            "🎭 Building high-performing teams:\n1. **Clarity** - Goals and roles\n2. **Trust** - Reliable and transparent\n3. **Autonomy** - Empower decisions\n4. **Growth** - Learning opportunities\n5. **Recognition** - Celebrate efforts\n\nWhat's working/not working in your team?"
        ];
        return teamResponses[Math.floor(Math.random() * teamResponses.length)];
    }

    // Motivation & Goals
    if (lowerMessage.includes('motivation') || lowerMessage.includes('goal') || lowerMessage.includes('focus') || lowerMessage.includes('overwhelm')) {
        const motivationResponses = [
            "🚀 Getting motivated:\n\n**Set Clear Goals:**\n- Big vision (1 year)\n- Medium goals (quarter)\n- Weekly objectives\n- Daily tasks\n\n**Keep Momentum:**\n- Track progress visually\n- Celebrate small wins\n- Review wins weekly\n- Share goals with others\n\n**Handle Overwhelm:**\n- Break into smaller steps\n- Do one task at a time\n- Take breaks\n- Ask for help\n\nWhat's your big goal?",
            "💫 Overcoming overwhelm:\n1. **Brain Dump** - Write everything down\n2. **Prioritize** - Top 3 only\n3. **Break Down** - Into mini-steps\n4. **Start Small** - Build momentum\n5. **One Thing** - Focus on now\n\nFeeling stuck on anything?",
            "✨ Goal achievement framework:\nS - Specific (clear definition)\nM - Measurable (track progress)\nA - Achievable (realistic)\nR - Relevant (aligns with values)\nT - Time-bound (deadline)\n\nWhat goal are we working towards?"
        ];
        return motivationResponses[Math.floor(Math.random() * motivationResponses.length)];
    }

    // Work-Life Balance
    if (lowerMessage.includes('balance') || lowerMessage.includes('burnout') || lowerMessage.includes('stress') || lowerMessage.includes('break')) {
        const balanceResponses = [
            "⚖️ Work-Life Balance Guide:\n\n**Boundaries:**\n- Set work hours\n- Notifications off after hours\n- Take real breaks\n- Vacation time = OFF time\n\n**Self-Care:**\n- Exercise regularly\n- Sleep 7-8 hours\n- Hobbies & interests\n- Time with family\n\n**Warning Signs:**\n- Constantly tired\n- Irritable\n- Losing interest\n- Skipping breaks\n\nHow are you doing?",
            "🧘 Preventing burnout:\n✓ Know your limits\n✓ Delegate tasks\n✓ Take mental breaks\n✓ Say no to extra work\n✓ Do things you love\n✓ Connect with others\n\nNeed to step back?",
            "🌟 Rest is productive!\n- Brain needs recovery\n- Creativity increases with breaks\n- Fresh perspective helps\n- Energy management matters\n\nWhen was your last real break?"
        ];
        return balanceResponses[Math.floor(Math.random() * balanceResponses.length)];
    }

    // Help & Support
    if (lowerMessage.includes('help') || lowerMessage.includes('what can you do') || lowerMessage.includes('capabilities') || lowerMessage.includes('?')) {
        const helpResponses = [
            "🤖 I can help you with:\n\n**📋 Task Management**\n- Organize your tasks\n- Prioritize effectively\n- Create schedules\n\n**📈 Productivity**\n- Time management techniques\n- Focus strategies\n- Productivity tools\n\n**🎯 Projects**\n- Project planning\n- Roadmaps & milestones\n- Risk management\n\n**👥 Teams**\n- Team communication\n- Collaboration tips\n- Leadership advice\n\n**⚖️ Work-Life Balance**\n- Burnout prevention\n- Stress management\n\nWhat would help most?",
            "✨ S T manger Assistant Features:\n- 💬 Real-time chat support\n- 📚 Knowledge & advice\n- 🎯 Goal-setting help\n- 📊 Productivity insights\n- 🤝 Team collaboration tips\n- ⏰ Time management strategies\n\nPick a topic to explore!",
            "👋 I'm your AI productivity coach! Ask me about:\n- Getting things done\n- Staying organized\n- Building teams\n- Managing time\n- Avoiding burnout\n- Achieving goals\n\nWhat's on your mind?"
        ];
        return helpResponses[Math.floor(Math.random() * helpResponses.length)];
    }

    // Deadline & Time
    if (lowerMessage.includes('deadline') || lowerMessage.includes('due') || lowerMessage.includes('urgent') || lowerMessage.includes('time')) {
        const timeResponses = [
            "⏰ Deadline Management:\n\n**When deadline is far:**\n- Break into phases\n- Set intermediate goals\n- Start early\n- Regular check-ins\n\n**When deadline is close:**\n- 80/20 rule (80% effort = 20% work)\n- Focus on essentials\n- Eliminate distractions\n- Work in sprints\n\n**Overdue tasks:**\n- Re-negotiate deadline\n- Ask for help\n- Communicate early\n- Create action plan\n\nWhat's your timeline?",
            "📅 Time management for deadlines:\n1. **Calculate backwards** from deadline\n2. **Buffer time** for unexpected issues\n3. **Mark milestones** along the way\n4. **Daily tracking** of progress\n5. **Escalate early** if at risk\n\nWhen's your deadline?",
            "🎯 Beat the clock:\n✓ Make deadline visible\n✓ Break into daily targets\n✓ Progress tracking\n✓ Risk contingency\n✓ Buffer time built-in\n\nHow much time do you have?"
        ];
        return timeResponses[Math.floor(Math.random() * timeResponses.length)];
    }

    // Default responses
    const defaultResponses = [
        "That's a great question! 🤔 Could you give me a bit more context? Are you asking about task management, productivity, projects, or team collaboration?",
        "Interesting! 💡 Tell me more - are you looking for advice on organizing, prioritizing, or planning something?",
        "I see! 👍 To give you better guidance, what area are you focusing on - getting more done, organizing better, or team productivity?",
        "Good point! 📝 I'd love to help more specifically. Is this about managing tasks, projects, productivity, or something else?",
        "That makes sense! 🎯 For more targeted advice, could you clarify - is this about work tasks, personal projects, or productivity in general?",
        "Absolutely! 💪 To help you best, let me know if you want tips on focus, organization, deadline management, or motivation?"
    ];

    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
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
        let exportText = 'S T manger Chat Export\n';
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
