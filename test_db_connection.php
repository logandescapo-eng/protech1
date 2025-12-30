<?php
// Simple test to check PostgreSQL connection
$host = '127.0.0.1';
$port = '5432';
$dbname = 'protech_db';
$user = 'postgres';
$pass = 'postgres123';

echo "Testing PostgreSQL Connection...\n\n";
echo "Host: $host\n";
echo "Port: $port\n";
echo "Database: $dbname\n";
echo "User: $user\n\n";

try {
    $dsn = "pgsql:host=$host;port=$port;dbname=$dbname";
    $conn = new PDO($dsn, $user, $pass);
    echo "✓ SUCCESS! Connected to PostgreSQL!\n";
    
    // Try a simple query
    $stmt = $conn->query("SELECT version();");
    $version = $stmt->fetchColumn();
    echo "✓ PostgreSQL Version: $version\n";
    
} catch (PDOException $e) {
    echo "✗ ERROR: " . $e->getMessage() . "\n";
    echo "\nError Code: " . $e->getCode() . "\n";
}
?>
