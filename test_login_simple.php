<?php
// Simple test to see if login is working
error_reporting(E_ALL);
ini_set('display_errors', 1);
session_start();

echo "<h2>Simple Login Test</h2>";

// Test database connection
require_once 'config.php';
if (!isset($conn)) {
    die("<p style='color:red;'>Database connection failed!</p>");
}
echo "<p style='color:green;'>✓ Database connected</p>";

// Test login
require_once 'auth_functions.php';

$test_email = 'john@example.com';
$test_password = 'password123';

echo "<p>Testing login with: $test_email</p>";

$result = login_user($test_email, $test_password);

echo "<h3>Result:</h3>";
echo "<pre>";
var_dump($result);
echo "</pre>";

echo "<h3>Session:</h3>";
echo "<pre>";
var_dump($_SESSION);
echo "</pre>";

if ($result['success']) {
    echo "<p style='color:green; font-size:20px;'>✓ LOGIN SUCCESS!</p>";
    echo "<p>Should redirect to: " . ($result['user_type'] === 'worker' ? 'worker.php' : 'user.php') . "</p>";
    echo "<p><a href='worker.php'>Test Worker Page</a> | <a href='user.php'>Test User Page</a></p>";
} else {
    echo "<p style='color:red; font-size:20px;'>✗ LOGIN FAILED: " . htmlspecialchars($result['message']) . "</p>";
}
?>
