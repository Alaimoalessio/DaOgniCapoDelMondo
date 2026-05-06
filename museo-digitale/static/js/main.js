/**
 * Da ogni capo del mondo - Museo Digitale
 * main.js — Global UI interactions, loaded on every page.
 *
 * Page-specific modules:
 *   collezione.js — AJAX filtering, filter dropdowns (collezione page only)
 */

document.addEventListener('DOMContentLoaded', function () {

    // ===== SHARED UTILITIES (exposed for collezione.js) =====

    /** Escape HTML to prevent XSS when injecting dynamic content */
    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * Resolve image path to a usable URL.
     * Mirrors the Flask image_url_filter: absolute URLs pass through,
     * relative paths are prefixed with /static/.
     */
    function resolveImageUrl(imagePath) {
        if (!imagePath) return '';
        if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
            return imagePath;
        }
        return `/static/${imagePath}`;
    }

    // ===== ITEM ANIMATIONS (IntersectionObserver) =====

    function applyItemAnimations(items) {
        if (!items || items.length === 0) return;
        if (!('IntersectionObserver' in window)) {
            items.forEach(item => {
                item.style.opacity = '1';
                item.style.transform = 'none';
                item.style.filter = 'none';
            });
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0) scale(1)';
                        entry.target.style.filter = 'blur(0px)';
                    }, index * 50);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

        items.forEach(item => {
            if (item.classList.contains('museum-item--skeleton')) return;
            item.style.opacity = '0';
            item.style.transform = 'translateY(28px) scale(0.96)';
            item.style.filter = 'blur(8px)';
            item.style.transition = 'opacity 0.55s cubic-bezier(0.4,0,0.2,1), transform 0.55s cubic-bezier(0.4,0,0.2,1), filter 0.55s ease';
            observer.observe(item);
        });
    }

    // Expose utilities for collezione.js (loaded after this file)
    window.MuseoUtils = { escapeHtml, resolveImageUrl, applyItemAnimations };

    // Apply animations to SSR-rendered items on page load
    applyItemAnimations(document.querySelectorAll('.museum-item:not(.museum-item--skeleton)'));


    // ===== LAZY IMAGE LOADING =====

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('loaded');
                    observer.unobserve(entry.target);
                }
            });
        });
        document.querySelectorAll('img[loading="lazy"]').forEach(img => imageObserver.observe(img));
    }


    // ===== PAGINATION: JUMP TO PAGE =====

    function jumpToPage() {
        const jumpInput = document.getElementById('jump-to-page');
        if (!jumpInput) return;

        const page    = parseInt(jumpInput.value, 10);
        const maxPage = parseInt(jumpInput.getAttribute('max'), 10);
        const url     = new URL(window.location.href);

        if (page >= 1 && page <= maxPage) {
            url.searchParams.set('page', page);
            window.location.href = url.toString();
        } else {
            jumpInput.setCustomValidity(`Inserisci un numero tra 1 e ${maxPage}`);
            jumpInput.reportValidity();
            setTimeout(() => jumpInput.setCustomValidity(''), 3000);
        }
    }

    window.jumpToPage = jumpToPage;

    const jumpInput = document.getElementById('jump-to-page');
    if (jumpInput) {
        jumpInput.addEventListener('keypress', e => {
            if (e.key === 'Enter') jumpToPage();
        });
    }


    // ===== SMOOTH SCROLL FOR IN-PAGE ANCHORS =====

    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                const offset = 100;
                window.scrollTo({
                    top: target.getBoundingClientRect().top + window.pageYOffset - offset,
                    behavior: 'smooth'
                });
            }
        });
    });


    // ===== SEARCH ENHANCEMENTS =====

    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                this.value = '';
                this.blur();
            }
        });

        // Press '/' to focus search (when not in a text field)
        document.addEventListener('keydown', function (e) {
            if (e.key === '/' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }


    // ===== LANGUAGE SWITCHER (backup handler) =====
    // Primary handler is inline in base.html; this is a safety net.
    const languageBtn  = document.getElementById('languageBtn');
    const languageMenu = document.getElementById('languageMenu');

    if (languageBtn && languageMenu) {
        document.addEventListener('click', function (e) {
            if (!languageBtn.contains(e.target) && !languageMenu.contains(e.target)) {
                languageMenu.classList.remove('active');
                languageBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }


    // ===== PARALLAX (gallery-header only) =====

    const parallaxTargets = document.querySelectorAll('.gallery-header');
    if (parallaxTargets.length > 0) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            parallaxTargets.forEach(el => {
                el.style.transform = `translateY(${scrolled * 0.25}px)`;
            });
        }, { passive: true });
    }

});
