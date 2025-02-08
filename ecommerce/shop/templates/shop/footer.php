<?php
// Footer section of the e-commerce website
?>

<footer>
    <div class="container">
        <p>&copy; <?php echo date("Y"); ?> Your Company Name. All rights reserved.</p>
        <ul>
            <li><a href="index.php">Home</a></li>
            <li><a href="products.php">Products</a></li>
            <li><a href="cart.php">Cart</a></li>
            <li><a href="contact.php">Contact Us</a></li>
        </ul>
    </div>
</footer>

<style>
    footer {
        background-color: #333;
        color: white;
        padding: 20px 0;
        text-align: center;
    }
    footer .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }
    footer ul {
        list-style: none;
        padding: 0;
    }
    footer ul li {
        display: inline;
        margin: 0 15px;
    }
    footer ul li a {
        color: white;
        text-decoration: none;
    }
    footer ul li a:hover {
        text-decoration: underline;
    }
</style>