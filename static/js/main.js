// Register Service Worker (if available)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js').catch(err => {
      console.warn('ServiceWorker registration failed:', err);
    });
  });
}

// Normalize any accidental API logout links in the DOM
document.addEventListener('DOMContentLoaded', () => {
  const fixLogoutHref = (a) => {
    try {
      const href = a.getAttribute('href') || '';
      if (!href) return;
      const isApiRel = href.includes('/api/users/logout/');
      let isApiAbs = false;
      try {
        const u = new URL(href, window.location.origin);
        isApiAbs = u.pathname === '/api/users/logout/';
      } catch (_) {}
      if (isApiRel || isApiAbs) {
        a.setAttribute('href', '/logout/');
      }
    } catch (_) {}
  };
  document.querySelectorAll('a').forEach(fixLogoutHref);
  // Also observe future DOM changes (e.g., SPA content) and fix dynamically
  const mo = new MutationObserver((mutations) => {
    for (const m of mutations) {
      m.addedNodes && m.addedNodes.forEach(node => {
        if (node && node.nodeType === 1) {
          if (node.tagName === 'A') fixLogoutHref(node);
          node.querySelectorAll && node.querySelectorAll('a').forEach(fixLogoutHref);
        }
      });
    }
  });
  mo.observe(document.documentElement, { childList: true, subtree: true });
});

// Optional: enhance logout to use API POST if available
window.handleLogout = async function (event) {
  if (event) {
    event.preventDefault();
  }
  try {
    if (!confirm('Are you sure you want to logout?')) return;
    
    // FIRST: Clear ALL browser storage IMMEDIATELY
    try {
      // Clear localStorage completely
      localStorage.clear();
      
      // Clear sessionStorage completely  
      sessionStorage.clear();
      
      // Also try to clear each known key
      const storageKeys = [
        'accessToken',
        'refreshToken',
        'userEmail',
        'rememberMe',
        'user',
        'profile',
        'token',
        'rememberedEmail'
      ];
      
      for (const key of storageKeys) {
        localStorage.removeItem(key);
        sessionStorage.removeItem(key);
      }
    } catch (_) {
      console.log('Storage clear failed');
    }
    
    // Clear all cookies BEFORE API call
    document.cookie.split(";").forEach(c => {
      const cookieName = c.split("=")[0].trim();
      if (cookieName) {
        document.cookie = `${cookieName}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 UTC; Max-Age=0; SameSite=Lax`;
        document.cookie = `${cookieName}=; Path=/api/; Expires=Thu, 01 Jan 1970 00:00:00 UTC; Max-Age=0; SameSite=Lax`;
      }
    });
    
  } catch (e) {
    console.error('Pre-logout cleanup error:', e);
  }
  
  // THEN: Call logout API
  try {
    await fetch('/api/users/logout/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || '',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    });
  } catch (e) {
    console.log('API logout failed');
  }
  
  // FINALLY: Redirect to logout endpoint
  setTimeout(() => {
    // Clear cookies one more time before redirect
    document.cookie.split(";").forEach(c => {
      const cookieName = c.split("=")[0].trim();
      if (cookieName) {
        document.cookie = `${cookieName}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 UTC`;
      }
    });
    window.location.href = '/logout/';
  }, 50);
}

// Defensive: intercept any accidental links to the API logout endpoint
document.addEventListener('click', (ev) => {
  const a = ev.target.closest && ev.target.closest('a');
  if (!a) return;
  try {
    const hrefAttr = a.getAttribute('href') || '';
    const hrefAbs = a.href || '';
    const matchesAttr = hrefAttr.includes('/api/users/logout/');
    let matchesAbs = false;
    try {
      const u = new URL(hrefAbs, window.location.origin);
      matchesAbs = u.pathname === '/api/users/logout/';
    } catch (_) {}
    if (matchesAttr || matchesAbs) {
      ev.preventDefault();
      return window.handleLogout(ev);
    }
  } catch (_) {}
});

// Footer notification count + footer button wiring
document.addEventListener('DOMContentLoaded', () => {
  const footerBtn = document.getElementById('footer-notif-btn');
  const footerCount = document.getElementById('footer-notif-count');

  async function loadFooterNotifCount() {
    try {
      // Prefer built window.API if available
      if (window.API && window.API.notifications && typeof window.API.notifications.getCount === 'function') {
        const data = await window.API.notifications.getCount();
        const count = data && (data.unread_count ?? data.count ?? 0);
        if (footerCount) {
          if (count > 0) {
            footerCount.textContent = count > 99 ? '99+' : String(count);
            footerCount.style.display = 'inline-block';
          } else {
            footerCount.style.display = 'none';
          }
        }
      } else {
        // Fallback: try fetching notifications and count unread
        const resp = await fetch('/api/notifications/?page_size=1', { credentials: 'include' });
        if (resp.ok) {
          const d = await resp.json();
          const unread = d.unread_count ?? (d.results ? d.results.filter(n => !n.is_read).length : 0);
          if (footerCount) {
            if (unread > 0) {
              footerCount.textContent = unread > 99 ? '99+' : String(unread);
              footerCount.style.display = 'inline-block';
            } else {
              footerCount.style.display = 'none';
            }
          }
        }
      }
    } catch (e) {
      console.warn('Failed to load footer notification count', e);
    }
  }

  // Wire footer button to open notifications panel
  if (footerBtn) {
    footerBtn.addEventListener('click', (e) => {
      e.preventDefault();
      try {
        if (window.NotificationCenter && typeof window.NotificationCenter.openNotifications === 'function') {
          window.NotificationCenter.openNotifications();
        } else {
          // try triggering existing header trigger
          const hdr = document.getElementById('notifications-trigger');
          hdr && hdr.click();
        }
      } catch (_) {}
    });
  }

  // initial load + poll
  loadFooterNotifCount();
  setInterval(loadFooterNotifCount, 30000);

  // Optional: toggle sidebar.expanded class when user toggles mobile/desktop open
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) {
    sidebar.addEventListener('mouseenter', () => sidebar.classList.add('expanded'));
    sidebar.addEventListener('mouseleave', () => sidebar.classList.remove('expanded'));
  }
});
