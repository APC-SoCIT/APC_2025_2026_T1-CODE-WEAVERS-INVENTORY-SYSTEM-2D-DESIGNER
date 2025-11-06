/**
 * Admin Security Client-Side Validation (optimized)
 * - Caches positive admin verification for 5 minutes
 * - Defers network work to idle time
 * - Prevents double initialization
 */

const ADMIN_CACHE_KEY = 'admin_status_v1';
const ADMIN_CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

function readAdminCache() {
    try {
        const raw = sessionStorage.getItem(ADMIN_CACHE_KEY);
        if (!raw) return null;
        const data = JSON.parse(raw);
        if (!data || typeof data !== 'object') return null;
        if (Date.now() - (data.timestamp || 0) > ADMIN_CACHE_TTL_MS) return null;
        return data;
    } catch (_) {
        return null;
    }
}

function writeAdminCache(isAdmin) {
    try {
        sessionStorage.setItem(ADMIN_CACHE_KEY, JSON.stringify({ is_admin: !!isAdmin, timestamp: Date.now() }));
    } catch (_) {
        // ignore storage errors
    }
}

// Central admin path list so monitoring can short-circuit on non-admin pages
const ADMIN_PATHS = [
    '/admin/',
    '/admin-dashboard',
    '/admin-products',
    '/admin-view-users',
    '/admin-view-processing-orders',
    '/admin-view-confirmed-orders',
    '/admin-view-shipping-orders',
    '/admin-view-delivered-orders',
    '/admin-view-booking',
];

// Check if user is trying to access admin dashboard
function checkAdminAccess() {
    const currentPath = window.location.pathname;

    // Check if current path is an admin path
    const isAdminPath = ADMIN_PATHS.some(path => currentPath.startsWith(path));

    if (!isAdminPath) return;

    // If server already indicates admin, skip verification entirely
    if (window.__is_admin__ === true) return;

    const cached = readAdminCache();
    if (cached && cached.is_admin === true) {
        return; // Skip network call within TTL
    }

    const verify = () => {
        fetch('/verify-admin-status/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (!data.is_admin) {
                // User is not admin, show warning and redirect
                showAccessDeniedModal();
                setTimeout(() => {
                    window.location.href = '/adminlogin';
                }, 3000);
            } else {
                writeAdminCache(true);
            }
        })
        .catch(error => {
            // Be non-disruptive on errors to avoid kicking logged-in admins
            console.warn('Admin verification failed, skipping client redirect:', error);
        });
    };

    if ('requestIdleCallback' in window) {
        requestIdleCallback(() => { verify(); }, { timeout: 2000 });
    } else {
        setTimeout(() => { verify(); }, 200);
    }
}

// Show access denied modal
function showAccessDeniedModal() {
    // Create modal HTML
    const modalHTML = `
        <div id="accessDeniedModal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                max-width: 400px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            ">
                <div style="color: #dc3545; font-size: 48px; margin-bottom: 20px;">
                    ⚠️
                </div>
                <h2 style="color: #dc3545; margin-bottom: 15px;">Access Denied</h2>
                <p style="margin-bottom: 20px; color: #666;">
                    You do not have administrator privileges to access this page.
                    You will be redirected to the login page.
                </p>
                <div style="
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                    color: #666;
                ">
                    Redirecting in <span id="countdown">3</span> seconds...
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    let countdown = 3;
    const countdownElement = document.getElementById('countdown');
    const countdownInterval = setInterval(() => {
        countdown--;
        if (countdownElement) countdownElement.textContent = String(countdown);
        if (countdown <= 0) clearInterval(countdownInterval);
    }, 1000);
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Monitor for navigation to admin pages (single init)
let __adminMonitorInitialized = false;
function monitorAdminAccess() {
    // If server says user is admin, skip all monitoring to cut overhead
    if (window.__is_admin__ === true) return;
    if (__adminMonitorInitialized) return;

    // Only initialize monitoring on admin paths to avoid overhead elsewhere
    const currentPath = window.location.pathname;
    const onAdminPath = ADMIN_PATHS.some(path => currentPath.startsWith(path));
    if (!onAdminPath) return;

    __adminMonitorInitialized = true;

    // Check on page load
    checkAdminAccess();

    // Monitor for programmatic navigation within admin area
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;

    history.pushState = function() {
        originalPushState.apply(history, arguments);
        setTimeout(checkAdminAccess, 100);
    };

    history.replaceState = function() {
        originalReplaceState.apply(history, arguments);
        setTimeout(checkAdminAccess, 100);
    };

    // Monitor for back/forward navigation
    window.addEventListener('popstate', () => {
        setTimeout(checkAdminAccess, 100);
    });
}

// Initialize security monitoring when DOM is ready (single path)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', monitorAdminAccess);
} else {
    monitorAdminAccess();
}
