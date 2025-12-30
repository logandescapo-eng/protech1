<?php
// Test login flow with detailed logging
error_reporting(E_ALL);
ini_set('display_errors', 1);
session_start();

echo "<h2>Login Flow Test</h2>";

// Test database connection first
require_once 'config.php';
if (!isset($conn)) {
    die("<p style='color:red;'>Database connection failed!</p>");
}
echo "<p style='color:green;'>✓ Database connected</p>";

// Test if user exists
require_once 'auth_functions.php';

echo "<h3>Testing with sample user:</h3>";
$test_email = 'john@example.com';
$test_password = 'password123';

echo "<p>Email: $test_email</p>";
echo "<p>Password: password123</p>";

$result = login_user($test_email, $test_password);

echo "<h3>Login Result:</h3>";
echo "<pre>";
print_r($result);
echo "</pre>";

echo "<h3>Session Data:</h3>";
echo "<pre>";
print_r($_SESSION);
echo "</pre>";

if ($result['success']) {
    echo "<p style='color:green; font-weight:bold;'>✓ Login successful!</p>";
    echo "<p>User Type: " . $result['user_type'] . "</p>";
    
    if ($result['user_type'] === 'worker') {
        echo "<p><a href='worker.php'>Go to Worker Dashboard (worker.php)</a></p>";
    } else {
        echo "<p><a href='user.php'>Go to User Dashboard (user.php)</a></p>";
    }
} else {
    echo "<p style='color:red; font-weight:bold;'>✗ Login failed: " . htmlspecialchars($result['message']) . "</p>";
}
?>
