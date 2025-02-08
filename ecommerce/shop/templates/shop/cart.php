<?php
session_start();
include 'includes/db.php';
include 'includes/header.php';

if (!isset($_SESSION['cart'])) {
    $_SESSION['cart'] = [];
}

if (isset($_POST['update_cart'])) {
    foreach ($_POST['quantity'] as $product_id => $quantity) {
        if ($quantity == 0) {
            unset($_SESSION['cart'][$product_id]);
        } else {
            $_SESSION['cart'][$product_id] = $quantity;
        }
    }
}

$total = 0;
?>

<div class="cart-container">
    <h1>Your Shopping Cart</h1>
    <form method="post" action="">
        <table>
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($_SESSION['cart'] as $product_id => $quantity): 
                    $product = getProductById($product_id); // Assume this function retrieves product details
                    $item_total = $product['price'] * $quantity;
                    $total += $item_total;
                ?>
                <tr>
                    <td><?php echo $product['name']; ?></td>
                    <td>
                        <input type="number" name="quantity[<?php echo $product_id; ?>]" value="<?php echo $quantity; ?>" min="0">
                    </td>
                    <td><?php echo number_format($product['price'], 2); ?></td>
                    <td><?php echo number_format($item_total, 2); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <div class="cart-total">
            <strong>Total: <?php echo number_format($total, 2); ?></strong>
        </div>
        <button type="submit" name="update_cart">Update Cart</button>
        <a href="checkout.php" class="checkout-button">Proceed to Checkout</a>
    </form>
</div>

<?php include 'includes/footer.php'; ?>