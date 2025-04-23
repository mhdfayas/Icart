// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    
// Add to cart functionality with animation
    const addToCartBtns = document.querySelectorAll('.add-to-cart');
    
    if (addToCartBtns) {
        addToCartBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const productId = this.getAttribute('data-product-id');
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // Show loading state
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                this.disabled = true;
                
                fetch('/cart/add/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        product_id: productId,
                        quantity: 1
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update cart count badge
                        const cartBadge = document.querySelector('.nav-icon .badge');
                        if (cartBadge) {
                            cartBadge.textContent = data.cart_count;
                        } else {
                            const cartIcon = document.querySelector('.nav-icon');
                            if (cartIcon) {
                                const newBadge = document.createElement('span');
                                newBadge.className = 'badge bg-primary rounded-pill';
                                newBadge.textContent = data.cart_count;
                                cartIcon.appendChild(newBadge);
                            }
                        }
                        
                        // Show success animation
                        this.innerHTML = '<i class="fas fa-check"></i>';
                        setTimeout(() => {
                            this.innerHTML = '<i class="fas fa-shopping-cart"></i> Add to Cart';
                            this.disabled = false;
                        }, 1500);
                        
                        // Show toast notification
                        const toast = new bootstrap.Toast(document.getElementById('cartToast'));
                        document.getElementById('toastProductName').textContent = data.product_name;
                        toast.show();
                    } else {
                        this.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error';
                        setTimeout(() => {
                            this.innerHTML = '<i class="fas fa-shopping-cart"></i> Add to Cart';
                            this.disabled = false;
                        }, 1500);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error';
                    setTimeout(() => {
                        this.innerHTML = '<i class="fas fa-shopping-cart"></i> Add to Cart';
                        this.disabled = false;
                    }, 1500);
                });
            });
        });
    }

    // Newsletter Form
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            const submitBtn = this.querySelector('button[type="submit"]');

const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            submitBtn.disabled = true;
            
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    email: emailInput.value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    submitBtn.innerHTML = '<i class="fas fa-check"></i> Subscribed';
                    emailInput.value = '';
                    
                    setTimeout(() => {
                        submitBtn.innerHTML = 'Subscribe';
                        submitBtn.disabled = false;
                    }, 2000);
                } else {
                    submitBtn.innerHTML = 'Subscribe';
                    submitBtn.disabled = false;
                    
                    // Show error message
                    alert(data.error || 'Something went wrong. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                submitBtn.innerHTML = 'Subscribe';
                submitBtn.disabled = false;
                alert('Something went wrong. Please try again.');
            });
        });
    }

    // Animate elements on scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fadeIn');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(el => {
            observer.observe(el);
        });
    }
});
// Function to update cart item quantity
function updateQuantity(input) {
    const itemId = input.getAttribute('data-item-id');
    const quantity = input.value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update item subtotal
            const subtotalEl = document.getElementById(`subtotal-${itemId}`);
            if (subtotalEl) {
                subtotalEl.textContent = data.item_subtotal;
            }
            
            // Update cart total
            const totalEl = document.getElementById('cart-total');
            if (totalEl) {
                totalEl.textContent = data.cart_total;
            }
        }
    })
    .catch(error => console.error('Error:', error));
}
