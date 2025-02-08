<?php
include 'includes/db.php';
include 'includes/header.php';

$products = getProducts(); // Function to retrieve products from the database

?>

<div class="container">
    <h1>Available Products</h1>
    <div class="product-list">
        <?php foreach ($products as $product): ?>
            <div class="product-item">
                <img src="assets/images/<?php echo $product['image']; ?>" alt="<?php echo $product['name']; ?>">
                <h2><?php echo $product['name']; ?></h2>
                <p><?php echo $product['description']; ?></p>
                <p>Price: $<?php echo number_format($product['price'], 2); ?></p>
                <button class="add-to-cart" data-id="<?php echo $product['id']; ?>">Add to Cart</button>
            </div>
        <?php endforeach; ?>
    </div>
</div>

<?php include 'includes/footer.php'; ?>