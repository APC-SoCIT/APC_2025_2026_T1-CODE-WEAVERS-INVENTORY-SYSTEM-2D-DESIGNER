document.addEventListener('DOMContentLoaded', function() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    const cartCount = document.getElementById('cart-count');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            addToCart(productId);
        });
    });

    function addToCart(productId) {
        // Simulate adding to cart
        let cart = JSON.parse(localStorage.getItem('cart')) || {};
        cart[productId] = (cart[productId] || 0) + 1;
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartCount();
    }

    function updateCartCount() {
        const cart = JSON.parse(localStorage.getItem('cart')) || {};
        const totalCount = Object.values(cart).reduce((sum, count) => sum + count, 0);
        cartCount.textContent = totalCount;
    }

    updateCartCount();
});