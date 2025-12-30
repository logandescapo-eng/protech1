<?php
// Router for PHP built-in server
// This ensures proper routing for PHP and HTML files

$requestUri = $_SERVER['REQUEST_URI'];
$requestPath = parse_url($requestUri, PHP_URL_PATH);

// Remove leading slash
$requestPath = ltrim($requestPath, '/');

// If the path is empty or root, serve index.html
if (empty($requestPath) || $requestPath === '/') {
    if (file_exists(__DIR__ . '/index.html')) {
        return false; // Let the server serve index.html
    }
}

// If the requested file exists, let PHP serve it
$filePath = __DIR__ . '/' . $requestPath;
if (file_exists($filePath) && is_file($filePath)) {
    return false; // Let PHP serve the file
}

// If it's a PHP file that doesn't exist, show 404
if (pathinfo($requestPath, PATHINFO_EXTENSION) === 'php') {
    http_response_code(404);
    echo "404 - File not found: " . htmlspecialchars($requestPath);
    return true;
}

// Default: let PHP handle it
return false;
?>

