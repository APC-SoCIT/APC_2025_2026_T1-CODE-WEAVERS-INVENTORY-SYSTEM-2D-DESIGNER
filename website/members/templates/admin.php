<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Admin Panel</title>
    <link rel="stylesheet" href="style.css"> 
</head>
<body>

    <header>
        <h1>E-commerce Admin Panel</h1>
        <nav>
            <ul>
                <li><a href="dashboard.php">Dashboard</a></li>
                <li><a href="products.php">Products</a></li>
                <li><a href="orders.php">Orders</a></li>
                <li><a href="customers.php">Customers</a></li>
                <li><a href="reports.php">Reports</a></li>
                <li><a href="settings.php">Settings</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section>
            <h2>Dashboard</h2>
            <div class="dashboard-stats">
                <div class="stat">
                    <h3>Total Orders</h3>
                    <p><?php echo 125; ?></p>
                </div>
                <div class="stat">
                    <h3>Total Sales</h3>
                    <p><?php echo '$15,000'; ?></p>
                </div>
                <div class="stat">
                    <h3>Total Customers</h3>
                    <p><?php echo 500; ?></p>
                </div>
            </div>
            <div class="charts">
                <h3>Sales Overview</h3>
                <canvas id="salesChart"></canvas> 
            </div>
        </section>
    </main>

    <footer>
        <p>&copy; <?php echo date('Y'); ?> Your E-commerce Store</p>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script> 
    <script src="script.js"></script> 

</body>
</html>
