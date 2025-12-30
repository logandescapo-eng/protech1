<?php
// Debug login script - add logging to see what's happening
error_reporting(E_ALL);
ini_set('display_errors', 1);

session_start();

require_once 'config.php';
require_once 'auth_functions.php';

echo "<h2>Login Debug</h2>";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'] ?? '';
    $password = $_POST['password'] ?? '';
    
    echo "<p>Email: " . htmlspecialchars($email) . "</p>";
    echo "<p>Password provided: " . (empty($password) ? 'NO' : 'YES') . "</p>";
    
    if (empty($email) || empty($password)) {
        echo "<p style='color: red;'>Error: Empty fields</p>";
        exit;
    }
    
    echo "<p>Attempting login...</p>";
    $result = login_user($email, $password);
    
    echo "<pre>";
    print_r($result);
    echo "</pre>";
    
    echo "<p>Session data:</p>";
    echo "<pre>";
    print_r($_SESSION);
    echo "</pre>";
    
    if ($result['success']) {
        echo "<p style='color: green;'>Login successful! User type: " . $result['user_type'] . "</p>";
        if ($result['user_type'] === 'worker') {
            echo "<p><a href='worker.php'>Go to Worker Dashboard</a></p>";
        } else {
            echo "<p><a href='user.php'>Go to User Dashboard</a></p>";
        }
    } else {
        echo "<p style='color: red;'>Login failed: " . htmlspecialchars($result['message']) . "</p>";
    }
} else {
    echo "<p>Please use POST method</p>";
}
?>
