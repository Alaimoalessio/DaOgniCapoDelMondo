/**
 * Da ogni capo del mondo - Museo Digitale
 * Main JavaScript - Dynamic Filtering and UI Interactions
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {

    // ===== DYNAMIC FILTERING =====
    const filterForm = document.getElementById('filterForm');
    const galleryGrid = document.getElementById('galleryGrid');

    if (filterForm && galleryGrid) {
        // Add change event listeners to all filter inputs
        const filterInputs = filterForm.querySelectorAll('input[type="radio"]');

        filterInputs.forEach(input => {
            input.addEventListener('change', function () {
                // Optional: Auto-submit on filter change
                // Uncomment the line below for instant filtering without clicking "Apply"
                // filterForm.submit();
            });
        });
    }


    // ===== LAZY LOADING FOR IMAGES =====
    const images = document.querySelectorAll('img[loading="lazy"]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.classList.add('loaded');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }


    // ===== SMOOTH SCROLL FOR NAVIGATION - Enhanced =====
    const navLinks = document.querySelectorAll('a[href^="#"]');

    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');

            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);

                if (target) {
                    const offset = 100; // Account for sticky navbar
                    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // ===== PARALLAX EFFECT FOR HERO SECTIONS =====
    const heroSections = document.querySelectorAll('.globe-overlay, .gallery-header');
    
    if (heroSections.length > 0) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            heroSections.forEach(section => {
                const rate = scrolled * 0.3;
                section.style.transform = `translateY(${rate}px)`;
            });
        });
    }

    // ===== CURSOR EFFECT FOR INTERACTIVE ELEMENTS =====
    const interactiveElements = document.querySelectorAll('a, button, .item-card, .filter-option');
    
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.cursor = 'pointer';
        });
    });


    // ===== FILTER DROPDOWN FUNCTIONALITY =====
    const filterDropdowns = document.querySelectorAll('.filter-dropdown');
    
    filterDropdowns.forEach(dropdown => {
        const btn = dropdown.querySelector('.filter-dropdown-btn');
        const menu = dropdown.querySelector('.filter-dropdown-menu');
        const options = menu.querySelectorAll('.filter-option');
        const selectedSpan = btn.querySelector('.filter-selected');
        
        // Toggle dropdown
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const isActive = this.classList.contains('active');
            
            // Close all other dropdowns
            filterDropdowns.forEach(d => {
                if (d !== dropdown) {
                    d.querySelector('.filter-dropdown-btn').classList.remove('active');
                    d.querySelector('.filter-dropdown-menu').classList.remove('active');
                }
            });
            
            // Toggle current dropdown
            this.classList.toggle('active');
            menu.classList.toggle('active');
        });
        
        // Update selected text when option is clicked
        options.forEach(option => {
            const input = option.querySelector('input[type="radio"]');
            const label = option.querySelector('span');
            
            input.addEventListener('change', function() {
                if (this.checked) {
                    selectedSpan.textContent = label.textContent;
                    // Close dropdown after selection
                    btn.classList.remove('active');
                    menu.classList.remove('active');
                }
            });
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.filter-dropdown')) {
            filterDropdowns.forEach(dropdown => {
                dropdown.querySelector('.filter-dropdown-btn').classList.remove('active');
                dropdown.querySelector('.filter-dropdown-menu').classList.remove('active');
            });
        }
    });

    // ===== MUSEUM ITEM ANIMATION ON SCROLL =====
    const museumItems = document.querySelectorAll('.museum-item');

    if (museumItems.length > 0 && 'IntersectionObserver' in window) {
        const itemObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0) scale(1)';
                        entry.target.style.filter = 'blur(0px)';
                    }, index * 50);

                    itemObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        museumItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(30px) scale(0.95)';
            item.style.filter = 'blur(10px)';
            item.style.transition = 'opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1), filter 0.6s ease';
            itemObserver.observe(item);
        });
    }


    // ===== AJAX FILTERING (Optional Enhancement) =====
    // Uncomment this section to enable dynamic filtering without page reload

    /*
    const filterForm = document.getElementById('filterForm');
    const galleryGrid = document.getElementById('galleryGrid');
    
    if (filterForm) {
        filterForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(filterForm);
            const params = new URLSearchParams(formData);
            
            try {
                const response = await fetch(`/api/filter?${params.toString()}`);
                const data = await response.json();
                
                // Clear current grid
                galleryGrid.innerHTML = '';
                
                // Add filtered items
                if (data.items && data.items.length > 0) {
                    data.items.forEach(item => {
                        const card = createItemCard(item);
                        galleryGrid.appendChild(card);
                    });
                } else {
                    galleryGrid.innerHTML = '<p class="no-results">Nessun oggetto trovato con i filtri selezionati.</p>';
                }
                
                // Update count
                const itemCount = document.querySelector('.item-count');
                if (itemCount) {
                    itemCount.textContent = `${data.count} oggetti trovati`;
                }
                
            } catch (error) {
                console.error('Error filtering items:', error);
            }
        });
    }
    
    // Helper function to create item card HTML
    function createItemCard(item) {
        const article = document.createElement('article');
        article.className = 'item-card';
        
        article.innerHTML = `
            <a href="/item/${item.id}" class="card-link">
                <div class="card-image">
                    <img src="${item.image_url}" alt="${item.title}" loading="lazy">
                    <div class="card-overlay">
                        <span class="view-details">Vedi dettagli →</span>
                    </div>
                </div>
                
                <div class="card-content">
                    <h3 class="card-title">${item.title}</h3>
                    
                    <div class="card-meta">
                        ${item.region ? `<span class="badge badge-region">${item.region}</span>` : ''}
                        ${item.era ? `<span class="badge badge-era">${item.era}</span>` : ''}
                    </div>
                    
                    <p class="card-description">${item.description.substring(0, 120)}...</p>
                </div>
            </a>
        `;
        
        return article;
    }
    */

    // ===== PAGINATION JUMP TO PAGE =====
    function jumpToPage() {
        const jumpInput = document.getElementById('jump-to-page');
        if (!jumpInput) return;
        
        const page = parseInt(jumpInput.value);
        const maxPage = parseInt(jumpInput.getAttribute('max'));
        const currentUrl = new URL(window.location.href);
        
        if (page >= 1 && page <= maxPage) {
            currentUrl.searchParams.set('page', page);
            // Preserve search query if exists
            const searchQuery = currentUrl.searchParams.get('q');
            if (searchQuery) {
                currentUrl.searchParams.set('q', searchQuery);
            }
            window.location.href = currentUrl.toString();
        } else {
            alert(`Inserisci un numero tra 1 e ${maxPage}`);
        }
    }
    
    // Make jumpToPage available globally
    window.jumpToPage = jumpToPage;
    
    // Add Enter key support for jump input
    const jumpInput = document.getElementById('jump-to-page');
    if (jumpInput) {
        jumpInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                jumpToPage();
            }
        });
    }

    // ===== LANGUAGE SWITCHER =====
    const languageBtn = document.getElementById('languageBtn');
    const languageMenu = document.getElementById('languageMenu');
    
    if (languageBtn && languageMenu) {
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!languageBtn.contains(e.target) && !languageMenu.contains(e.target)) {
                languageMenu.style.opacity = '0';
                languageMenu.style.visibility = 'hidden';
            }
        });
        
        // Toggle menu on button click
        languageBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const isVisible = languageMenu.style.visibility === 'visible';
            languageMenu.style.opacity = isVisible ? '0' : '1';
            languageMenu.style.visibility = isVisible ? 'hidden' : 'visible';
        });
    }

    // ===== SEARCH ENHANCEMENTS =====
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        // Clear search on Escape key
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                this.blur();
            }
        });
        
        // Auto-focus search on '/' key (when not in input)
        document.addEventListener('keydown', function(e) {
            if (e.key === '/' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }
});
