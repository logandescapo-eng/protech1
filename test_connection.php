<?php
// Test database connection and PHP extensions
echo "<h2>PHP Configuration Test</h2>";

echo "<h3>PHP Version:</h3>";
echo "<p>" . phpversion() . "</p>";

echo "<h3>Loaded Extensions:</h3>";
$extensions = get_loaded_extensions();
echo "<pre>";
echo "pdo: " . (extension_loaded('pdo') ? '✓ Loaded' : '✗ Not Loaded') . "\n";
echo "pdo_pgsql: " . (extension_loaded('pdo_pgsql') ? '✓ Loaded' : '✗ Not Loaded') . "\n";
echo "pgsql: " . (extension_loaded('pgsql') ? '✓ Loaded' : '✗ Not Loaded') . "\n";
echo "</pre>";

echo "<h3>PHP.ini Location:</h3>";
echo "<p>" . php_ini_loaded_file() . "</p>";

echo "<h3>PDO Drivers Available:</h3>";
echo "<pre>";
print_r(PDO::getAvailableDrivers());
echo "</pre>";

echo "<h3>Testing Database Connection:</h3>";
require_once 'config.php';
if (isset($conn)) {
    echo "<p style='color: green;'>✓ Database connection successful!</p>";
} else {
    echo "<p style='color: red;'>✗ Database connection failed</p>";
}
?>
