(function () {
    function liveBase() {
        var url = (window.PROTECH_LIVE_URL || '').trim().replace(/\/$/, '');
        return url || null;
    }

    function pagesBase() {
        var meta = document.querySelector('meta[name="protech-pages-root"]');
        return meta ? meta.content : '';
    }

    window.appUrl = function (path) {
        path = path || '/';
        if (!path.startsWith('/')) {
            path = '/' + path;
        }
        var base = liveBase();
        if (base) {
            return base + path;
        }
        if (path === '/auth' || path.indexOf('/auth') === 0) {
            var qs = path.indexOf('?') >= 0 ? path.slice(path.indexOf('?')) : '';
            return pagesBase() + 'auth.html' + qs;
        }
        return pagesBase() + 'index.html';
    };

    window.redirectToApp = function (path) {
        window.location.replace(appUrl(path));
    };

    function rewriteLinks() {
        document.querySelectorAll('[data-app-href]').forEach(function (el) {
            el.setAttribute('href', appUrl(el.getAttribute('data-app-href')));
        });
        document.querySelectorAll('a[href="/auth.html"], a[href="auth.html"]').forEach(function (el) {
            el.setAttribute('href', appUrl('/auth'));
        });
    }

    function setupBanner() {
        if (liveBase()) {
            return;
        }
        var bar = document.createElement('div');
        bar.setAttribute('role', 'status');
        bar.style.cssText = 'background:#fef3c7;color:#92400e;padding:12px 16px;text-align:center;font-size:14px;border-bottom:1px solid #fcd34d;';
        bar.innerHTML = 'Preview on GitHub Pages: sign-in and dashboards need the live Flask app. '
            + 'Deploy on <a href="https://railway.app">Railway</a> or <a href="https://render.com">Render</a>, '
            + 'then set <code>PROTECH_LIVE_URL</code> in <code>live-config.js</code>.';
        document.body.insertBefore(bar, document.body.firstChild);
    }

    function init() {
        rewriteLinks();
        setupBanner();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
