<?php
require_once __DIR__ . '/../functions.php';
secure_session_start();
session_destroy();
header('Location: /');
exit;
