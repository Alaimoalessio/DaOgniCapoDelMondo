/**
 * Da ogni capo del mondo - Museo Digitale
 * collezione.js — AJAX filtering, skeleton screens, filter dropdowns.
 * Loaded only on the /collezione page (via {% block scripts %} in collezione.html).
 * Depends on window.MuseoUtils exposed by main.js.
 */

document.addEventListener('DOMContentLoaded', function () {

    // Wait for MuseoUtils (main.js sets it before DOMContentLoaded fires on the
    // same tick, but be defensive in case load order changes)
    var utils = window.MuseoUtils || {
        escapeHtml: function(s) {
            if (!s) return '';
            return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
        },
        resolveImageUrl: function(p) {
            if (!p) return '';
            return (p.startsWith('http://') || p.startsWith('https://')) ? p : '/static/' + p;
        },
        applyItemAnimations: function() {}
    };

    var escapeHtml       = utils.escapeHtml;
    var resolveImageUrl  = utils.resolveImageUrl;
    var applyItemAnimations = utils.applyItemAnimations;

    const filterForm     = document.getElementById('filterForm');
    const galleryGrid    = document.getElementById('galleryGrid');
    const loadingOverlay = document.getElementById('galleryLoadingOverlay');

    // ===== SKELETON CARDS =====

    /** Build one skeleton card matching .museum-item markup */
    function buildSkeletonCard() {
        return `<article class="museum-item museum-item--skeleton" aria-hidden="true">
            <div class="museum-item-link">
                <div class="museum-image-wrapper"></div>
            </div>
        </article>`;
    }

    /** Show N skeleton cards in the gallery grid */
    function showSkeletons(count) {
        if (!galleryGrid) return;
        galleryGrid.innerHTML = Array.from({ length: count }, buildSkeletonCard).join('');
    }


    // ===== ITEM CARD BUILDER =====

    /** Build a gallery card from a JSON item (mirrors collezione.html markup) */
    function buildItemCard(item) {
        const imgSrc   = escapeHtml(resolveImageUrl(item.image_url));
        const title    = escapeHtml(item.title || '');
        // A11y #21: descriptive alt text — mirrors the Jinja2 template format
        const altParts = [item.title, item.category, item.region, item.era,
                          item.year_from ? (item.year_from + (item.year_to && item.year_to !== item.year_from ? ' – ' + item.year_to : '')) : null]
                         .filter(Boolean);
        const imgAlt   = escapeHtml(altParts.join(', '));
        const region   = item.region   ? `<span class="badge badge-region">${escapeHtml(item.region)}</span>`   : '';
        const era      = item.era      ? `<span class="badge badge-era">${escapeHtml(item.era)}</span>`         : '';
        const category = item.category ? `<span class="badge badge-category">${escapeHtml(item.category)}</span>` : '';
        const hasBadges = item.region || item.era || item.category;
        const rawDesc  = item.description || '';
        const snippet  = rawDesc.length > 150 ? rawDesc.substring(0, 150) + '…' : rawDesc;
        const descHtml = snippet ? `<p class="museum-item-description">${escapeHtml(snippet)}</p>` : '';

        return `<article class="museum-item">
            <a href="/item/${item.id}" class="museum-item-link">
                <div class="museum-image-wrapper">
                    <img src="${imgSrc}" alt="${imgAlt}" loading="lazy" class="museum-image">
                    <div class="museum-overlay">
                        <div class="museum-overlay-content">
                            <h3 class="museum-item-title">${title}</h3>
                            ${hasBadges ? `<div class="museum-item-meta">${region}${era}${category}</div>` : ''}
                            ${descHtml}
                            <span class="museum-view-details">Clicca per dettagli →</span>
                        </div>
                    </div>
                </div>
            </a>
        </article>`;
    }


    // ===== PAGINATION BUILDER =====

    /** Build enhanced pagination HTML from the API response */
    function buildPaginationHtml(data, paramString) {
        if (!data || data.pages <= 1) return '';

        const { page, pages, has_prev, has_next, count } = data;

        function pageUrl(p) {
            const params = new URLSearchParams(paramString);
            params.set('page', p);
            return `/collezione?${params.toString()}`;
        }

        const start = Math.max(1, page - 2);
        const end   = Math.min(pages, page + 2);
        let numbersHtml = '';

        if (start > 1) {
            numbersHtml += `<a href="${pageUrl(1)}" class="pagination-number">1</a>`;
            if (start > 2) numbersHtml += `<span class="pagination-ellipsis">…</span>`;
        }
        for (let p = start; p <= end; p++) {
            numbersHtml += p === page
                ? `<span class="pagination-number active">${p}</span>`
                : `<a href="${pageUrl(p)}" class="pagination-number">${p}</a>`;
        }
        if (end < pages) {
            if (end < pages - 1) numbersHtml += `<span class="pagination-ellipsis">…</span>`;
            numbersHtml += `<a href="${pageUrl(pages)}" class="pagination-number">${pages}</a>`;
        }

        const firstBtn = page > 1     ? `<a href="${pageUrl(1)}"      class="pagination-btn pagination-first" title="Prima pagina"><span>«</span></a>`      : `<span class="pagination-btn pagination-first disabled"><span>«</span></span>`;
        const prevBtn  = has_prev     ? `<a href="${pageUrl(page-1)}"  class="pagination-btn pagination-prev"  title="Pagina precedente"><span>‹</span></a>` : `<span class="pagination-btn pagination-prev disabled"><span>‹</span></span>`;
        const nextBtn  = has_next     ? `<a href="${pageUrl(page+1)}"  class="pagination-btn pagination-next"  title="Pagina successiva"><span>›</span></a>`  : `<span class="pagination-btn pagination-next disabled"><span>›</span></span>`;
        const lastBtn  = page < pages ? `<a href="${pageUrl(pages)}"   class="pagination-btn pagination-last"  title="Ultima pagina"><span>»</span></a>`      : `<span class="pagination-btn pagination-last disabled"><span>»</span></span>`;

        return `<div class="pagination-enhanced" id="paginationEnhanced">
            <div class="container">
                <div class="pagination-wrapper">
                    ${firstBtn}${prevBtn}
                    <div class="pagination-numbers">${numbersHtml}</div>
                    ${nextBtn}${lastBtn}
                </div>
                <div class="pagination-info">
                    <span>Pagina ${page} di ${pages}</span>
                    <span class="pagination-separator">|</span>
                    <span>${count} oggetti totali</span>
                </div>
            </div>
        </div>`;
    }


    // ===== AJAX FILTERING =====

    if (filterForm && galleryGrid) {
        filterForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = new FormData(filterForm);
            const params   = new URLSearchParams(formData);

            // Carry over the active search query from the current URL
            const currentSearch = new URLSearchParams(window.location.search).get('q');
            if (currentSearch) params.set('q', currentSearch);

            // Show skeletons matching current visible count (default 12)
            const visibleItems = galleryGrid.querySelectorAll('.museum-item:not(.museum-item--skeleton)').length;
            showSkeletons(visibleItems || 12);
            if (loadingOverlay) loadingOverlay.classList.add('is-active');

            // Push URL immediately so back button works
            history.pushState({ filterParams: params.toString() }, '', `/collezione?${params.toString()}`);

            try {
                const response = await fetch(`/api/filter?${params.toString()}`);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const data = await response.json();

                if (data.items && data.items.length > 0) {
                    galleryGrid.innerHTML = data.items.map(buildItemCard).join('');
                    applyItemAnimations(galleryGrid.querySelectorAll('.museum-item'));
                } else {
                    galleryGrid.innerHTML = `
                        <div class="no-results" style="grid-column:1/-1;text-align:center;padding:var(--spacing-2xl) 0;">
                            <p style="font-size:1.25rem;color:var(--text-primary);margin-bottom:var(--spacing-sm);">Nessun oggetto trovato</p>
                            <p style="color:var(--text-secondary);">Prova a modificare o azzerare i filtri di ricerca.</p>
                        </div>`;
                }

                // Update item count badge
                const itemCount = document.querySelector('.item-count');
                if (itemCount) itemCount.textContent = `${data.count} oggetti`;

                // Replace pagination
                const existingPagination = document.getElementById('paginationEnhanced')
                    || document.querySelector('.pagination-enhanced');
                const paginationHtml = buildPaginationHtml(data, params.toString());

                if (existingPagination) {
                    if (paginationHtml) {
                        existingPagination.outerHTML = paginationHtml;
                    } else {
                        existingPagination.remove();
                    }
                } else if (paginationHtml) {
                    galleryGrid.insertAdjacentHTML('afterend', paginationHtml);
                }

            } catch (err) {
                console.error('[Filter] AJAX error — falling back to full reload:', err);
                filterForm.submit();
            } finally {
                if (loadingOverlay) loadingOverlay.classList.remove('is-active');
            }
        });

        // On back/forward, reload to restore SSR state
        window.addEventListener('popstate', () => window.location.reload());
    }

    // Show loading skeleton when the search form submits (full SSR reload)
    const searchForm = document.querySelector('.search-form');
    if (searchForm && galleryGrid) {
        searchForm.addEventListener('submit', () => {
            showSkeletons(12);
            if (loadingOverlay) loadingOverlay.classList.add('is-active');
        });
    }


    // ===== FILTER DROPDOWN UI =====

    const filterDropdowns = document.querySelectorAll('.filter-dropdown');

    filterDropdowns.forEach(dropdown => {
        const btn          = dropdown.querySelector('.filter-dropdown-btn');
        const menu         = dropdown.querySelector('.filter-dropdown-menu');
        const options      = menu.querySelectorAll('.filter-option');
        const selectedSpan = btn.querySelector('.filter-selected');

        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const isActive = this.classList.contains('active');

            filterDropdowns.forEach(d => {
                if (d !== dropdown) {
                    d.querySelector('.filter-dropdown-btn').classList.remove('active');
                    d.querySelector('.filter-dropdown-menu').classList.remove('active');
                }
            });

            this.classList.toggle('active', !isActive);
            menu.classList.toggle('active', !isActive);
        });

        options.forEach(option => {
            const input = option.querySelector('input[type="radio"]');
            const label = option.querySelector('span');

            input.addEventListener('change', function () {
                if (this.checked) {
                    selectedSpan.textContent = label.textContent;
                    btn.classList.remove('active');
                    menu.classList.remove('active');
                }
            });
        });
    });

    // Close all dropdowns when clicking outside
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.filter-dropdown')) {
            filterDropdowns.forEach(d => {
                d.querySelector('.filter-dropdown-btn').classList.remove('active');
                d.querySelector('.filter-dropdown-menu').classList.remove('active');
            });
        }
    });

    // ── A11y #20: Focus-visible fallback for browsers without :has() ────────
    const supportsHas = CSS.supports('selector(:has(*))');
    if (!supportsHas) {
        document.querySelectorAll('.filter-option input[type="radio"]').forEach(radio => {
            radio.addEventListener('focus', function () {
                this.closest('.filter-option').classList.add('has-focus-visible');
            });
            radio.addEventListener('blur', function () {
                this.closest('.filter-option').classList.remove('has-focus-visible');
            });
        });
    }

});
