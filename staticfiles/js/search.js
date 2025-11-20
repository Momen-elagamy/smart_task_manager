/**
 * Global Search System
 * Real-time search with debouncing across tasks, projects, and users
 */

let searchDebounceTimer = null;
const SEARCH_DEBOUNCE_DELAY = 300; // ms
const MIN_SEARCH_LENGTH = 2;

function initializeSearch() {
    const searchInput = document.getElementById('global-search-input') || document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput) {
        console.warn('Search input not found');
        return;
    }
    
    // Input event with debouncing
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        // Clear previous timer
        clearTimeout(searchDebounceTimer);
        
        if (query.length < MIN_SEARCH_LENGTH) {
            hideSearchResults();
            return;
        }
        
        // Debounce search
        searchDebounceTimer = setTimeout(() => {
            performSearch(query);
        }, SEARCH_DEBOUNCE_DELAY);
    });
    
    // Close on Escape
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hideSearchResults();
            searchInput.blur();
        }
    });
    
    // Close when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            hideSearchResults();
        }
    });
    
    console.log('Search initialized');
}

async function performSearch(query) {
    const searchResults = document.getElementById('search-results');
    
    if (!searchResults) return;
    
    try {
        // Show loading
        searchResults.innerHTML = '<div class="search-loading">Searching...</div>';
        searchResults.style.display = 'block';
        
        // Call API
        const data = await window.API.search.global(query, 'all', 20);
        
        // Display results
        displaySearchResults(data, query);
        
    } catch (error) {
        console.error('Search error:', error);
        searchResults.innerHTML = '<div class="search-no-results">Error searching. Please try again.</div>';
    }
}

function displaySearchResults(data, query) {
    const searchResults = document.getElementById('search-results');
    
    if (!data || data.total === 0) {
        searchResults.innerHTML = `
            <div class="search-no-results">
                <i class="fas fa-search" style="font-size: 32px; margin-bottom: 12px; opacity: 0.3;"></i>
                <p>No results found for "${escapeHtml(query)}"</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Tasks Section
    if (data.tasks && data.tasks.length > 0) {
        html += '<div class="search-section">';
        html += '<div class="search-section-title">Tasks</div>';
        data.tasks.forEach(task => {
            html += createSearchItem({
                type: 'task',
                icon: 'fa-tasks',
                title: task.title,
                meta: task.description ? truncate(task.description, 60) : 'No description',
                url: task.url
            });
        });
        html += '</div>';
    }
    
    // Projects Section
    if (data.projects && data.projects.length > 0) {
        html += '<div class="search-section">';
        html += '<div class="search-section-title">Projects</div>';
        data.projects.forEach(project => {
            html += createSearchItem({
                type: 'project',
                icon: 'fa-folder',
                title: project.name,
                meta: project.description ? truncate(project.description, 60) : 'No description',
                url: project.url
            });
        });
        html += '</div>';
    }
    
    // Users Section (admin/manager only)
    if (data.users && data.users.length > 0) {
        html += '<div class="search-section">';
        html += '<div class="search-section-title">Users</div>';
        data.users.forEach(user => {
            html += createSearchItem({
                type: 'user',
                icon: 'fa-user',
                title: user.name,
                meta: user.email,
                url: user.url
            });
        });
        html += '</div>';
    }
    
    searchResults.innerHTML = html;
    searchResults.style.display = 'block';
    
    // Add click handlers
    searchResults.querySelectorAll('.search-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const url = item.dataset.url;
            if (url) {
                window.location.href = url;
            }
        });
    });
}

function createSearchItem({ type, icon, title, meta, url }) {
    return `
        <div class="search-item" data-url="${escapeHtml(url)}">
            <div class="search-item-icon ${type}">
                <i class="fas ${icon}"></i>
            </div>
            <div class="search-item-content">
                <div class="search-item-title">${highlightText(escapeHtml(title))}</div>
                <div class="search-item-meta">${escapeHtml(meta)}</div>
            </div>
        </div>
    `;
}

function hideSearchResults() {
    const searchResults = document.getElementById('search-results');
    if (searchResults) {
        searchResults.style.display = 'none';
        searchResults.innerHTML = '';
    }
}

function highlightText(text) {
    const searchInput = document.getElementById('global-search-input') || document.getElementById('search-input');
    if (!searchInput) return text;
    
    const query = searchInput.value.trim();
    if (!query) return text;
    
    const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
    return text.replace(regex, '<mark style="background: rgba(6, 182, 212, 0.3); color: inherit; padding: 0 2px; border-radius: 2px;">$1</mark>');
}

function truncate(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSearch);
} else {
    initializeSearch();
}
