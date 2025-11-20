/**
 * Theme Management
 * Handles dark/light mode switching
 */

class ThemeManager {
    constructor() {
        this.currentTheme = this.getSavedTheme() || 'light';
        this.init();
    }

    init() {
        // Apply saved theme
        this.applyTheme(this.currentTheme);
        
        // Create theme toggle button if it doesn't exist
        if (!document.querySelector('.theme-toggle')) {
            this.createToggleButton();
        }
        
        // Listen for system theme changes
        this.watchSystemTheme();
    }

    getSavedTheme() {
        return localStorage.getItem('theme') || this.getSystemTheme();
    }

    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);
        
        // Update toggle button icon
        this.updateToggleIcon();
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    createToggleButton() {
        const button = document.createElement('button');
        button.className = 'theme-toggle';
        button.setAttribute('aria-label', 'Toggle theme');
        button.setAttribute('title', 'Toggle dark/light mode');
        button.innerHTML = this.currentTheme === 'dark' ? '☀️' : '🌙';
        
        button.addEventListener('click', () => this.toggleTheme());
        
        document.body.appendChild(button);
    }

    updateToggleIcon() {
        const button = document.querySelector('.theme-toggle');
        if (button) {
            button.innerHTML = this.currentTheme === 'dark' ? '☀️' : '🌙';
        }
    }

    watchSystemTheme() {
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    this.applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    }
}

/**
 * Keyboard Shortcuts Manager
 */
class KeyboardShortcutsManager {
    constructor() {
        this.shortcuts = {
            // Global shortcuts
            'ctrl+k': { action: 'search', description: 'Quick search' },
            'ctrl+n': { action: 'newTask', description: 'New task' },
            'ctrl+shift+n': { action: 'newProject', description: 'New project' },
            'ctrl+/': { action: 'showHelp', description: 'Show shortcuts' },
            'esc': { action: 'closeModal', description: 'Close modal' },
            
            // Navigation
            'g+d': { action: 'gotoDashboard', description: 'Go to dashboard' },
            'g+t': { action: 'gotoTasks', description: 'Go to tasks' },
            'g+p': { action: 'gotoProjects', description: 'Go to projects' },
            'g+c': { action: 'gotoChat', description: 'Go to chat' },
            
            // Task actions
            '?': { action: 'showHelp', description: 'Show help' },
        };
        
        this.sequenceKeys = [];
        this.sequenceTimeout = null;
        
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        this.createHelpModal();
    }

    handleKeyPress(e) {
        // Ignore if typing in input/textarea
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) {
            return;
        }

        // Build shortcut key string
        let shortcut = '';
        if (e.ctrlKey) shortcut += 'ctrl+';
        if (e.shiftKey) shortcut += 'shift+';
        if (e.altKey) shortcut += 'alt+';
        
        const key = e.key.toLowerCase();
        
        // Handle sequence shortcuts (like g+d)
        if (this.sequenceKeys.length > 0) {
            shortcut = `${this.sequenceKeys[0]}+${key}`;
            this.sequenceKeys = [];
            clearTimeout(this.sequenceTimeout);
        } else {
            shortcut += key;
        }

        // Check if this is a registered shortcut
        if (this.shortcuts[shortcut]) {
            e.preventDefault();
            this.executeAction(this.shortcuts[shortcut].action);
        } else if (key === 'g' && !e.ctrlKey && !e.shiftKey) {
            // Start sequence
            this.sequenceKeys = ['g'];
            this.sequenceTimeout = setTimeout(() => {
                this.sequenceKeys = [];
            }, 1000);
        }
    }

    executeAction(action) {
        switch (action) {
            case 'search':
                this.focusSearch();
                break;
            case 'newTask':
                if (typeof window.openTaskModal === 'function') {
                    window.openTaskModal();
                }
                break;
            case 'newProject':
                if (typeof window.openAddProjectModal === 'function') {
                    window.openAddProjectModal();
                }
                break;
            case 'showHelp':
                this.showHelpModal();
                break;
            case 'closeModal':
                this.closeAllModals();
                break;
            case 'gotoDashboard':
                window.location.href = '/dashboard/';
                break;
            case 'gotoTasks':
                window.location.href = '/tasks/';
                break;
            case 'gotoProjects':
                window.location.href = '/projects/';
                break;
            case 'gotoChat':
                window.location.href = '/chat/';
                break;
        }
    }

    focusSearch() {
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="Search"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    createHelpModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'shortcuts-help-modal';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h2>⌨️ Keyboard Shortcuts</h2>
                    <button class="close-btn" onclick="this.closest('.modal').classList.remove('active')">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="shortcuts-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        ${Object.entries(this.shortcuts).map(([key, shortcut]) => `
                            <div class="shortcut-item" style="padding: 0.5rem; border-bottom: 1px solid var(--border-color);">
                                <kbd style="background: var(--bg-secondary); padding: 0.25rem 0.5rem; border-radius: 4px; font-family: monospace;">${key}</kbd>
                                <span style="margin-left: 0.5rem; color: var(--text-secondary);">${shortcut.description}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    showHelpModal() {
        const modal = document.getElementById('shortcuts-help-modal');
        if (modal) {
            modal.classList.add('active');
        }
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeManager = new ThemeManager();
        window.keyboardShortcuts = new KeyboardShortcutsManager();
    });
} else {
    window.themeManager = new ThemeManager();
    window.keyboardShortcuts = new KeyboardShortcutsManager();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ThemeManager, KeyboardShortcutsManager };
}
