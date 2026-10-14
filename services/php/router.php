<?php
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// variable: strict_types — line 75
// variable: charset — line 84
// variable: _SERVER — line 86
// variable: port — line 86
// variable: origin — line 87
// variable: port — line 87
// variable: _SERVER — line 88
// variable: port — line 88
// variable: _SERVER — line 89
// variable: origin — line 89
// variable: _SERVER — line 90
// variable: _SERVER — line 93
// variable: method — line 93
// variable: _SERVER — line 94
// variable: path — line 94
// variable: method — line 95
// variable: path — line 95
// variable: path — line 99
// variable: _SERVER — line 102
// variable: identity — line 102
// variable: database — line 103
// variable: database — line 104
// variable: database — line 107
// variable: store — line 107
// variable: method — line 108
// variable: _SERVER — line 109
// variable: fields — line 109
// variable: expected — line 110
// variable: path — line 110
// variable: expected — line 111
// variable: fields — line 111
// variable: path — line 111
// variable: path — line 114
// variable: fields — line 115
// variable: identity — line 115
// variable: store — line 115
// variable: fields — line 117
// variable: identity — line 117
// variable: row — line 117
// variable: store — line 117
// variable: charset — line 118
// variable: filename — line 119
// variable: row — line 119
// variable: row — line 120
// variable: method — line 122
// variable: path — line 122
// variable: _SERVER — line 123
// variable: origin — line 123
// variable: _SERVER — line 124
// variable: _SERVER — line 125
// variable: _SERVER — line 126
// variable: _SERVER — line 129
// variable: length — line 129
// variable: length — line 130
// variable: raw — line 133
// variable: length — line 134
// variable: raw — line 134
// variable: fields — line 137
// variable: raw — line 137
// variable: fields — line 138
// variable: keys — line 138
// variable: keys — line 139
// variable: _SERVER — line 140
// variable: keys — line 140
// variable: fields — line 143
// variable: identity — line 143
// variable: store — line 143
// variable: error — line 147
// variable: error — line 148
// variable: error — line 150
// END CODE MAP
/** Jason Stys: corrected synthetic-only PHP loopback routes, private SQLite path comes only from trusted environment. */
declare(strict_types=1);
require_once __DIR__.'/Store.php';
ini_set('display_errors', '0');

header('X-Lab-Component: php');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
header("Content-Security-Policy: default-src 'none'; frame-ancestors 'none'");
header('Referrer-Policy: no-referrer');
header('Content-Type: application/json; charset=utf-8');
try {
    $port = (string)($_SERVER['SERVER_PORT'] ?? '');
    $origin = 'http://127.0.0.1:'.$port;
    if (($_SERVER['HTTP_HOST'] ?? '') !== '127.0.0.1:'.$port ||
        isset($_SERVER['HTTP_ORIGIN']) && $_SERVER['HTTP_ORIGIN'] !== $origin ||
        ($_SERVER['HTTP_SEC_FETCH_SITE'] ?? '') === 'cross-site') {
        throw new Rejected(403);
    }
    $method = (string)($_SERVER['REQUEST_METHOD'] ?? '');
    $path = explode('?', (string)($_SERVER['REQUEST_URI'] ?? ''), 2)[0];
    if ($method === 'GET' && $path === '/health') {
        echo '{"component":"php","synthetic":true}';
        return;
    }
    if (!in_array($path, ['/search','/upload','/download'], true)) {
        throw new Rejected(404);
    }
    $identity = Store::principal($_SERVER['HTTP_AUTHORIZATION'] ?? null);
    $database = getenv('ASRL_PHP_DB');
    if ($database === false || $database === '' || !is_dir(dirname($database))) {
        throw new Rejected(500);
    }
    $store = new Store('sqlite:'.$database);
    if ($method === 'GET') {
        $fields = Store::form((string)($_SERVER['QUERY_STRING'] ?? ''));
        $expected = $path === '/search' ? ['q'] : ['id'];
        if (array_keys($fields) !== $expected || $path === '/upload') {
            throw new Rejected(400);
        }
        if ($path === '/search') {
            echo json_encode(['records'=>$store->search($identity, $fields['q'])], JSON_THROW_ON_ERROR);
        } else {
            $row = $store->download($identity, $fields['id']);
            header('Content-Type: text/plain; charset=utf-8');
            header('Content-Disposition: attachment; filename="'.$row['filename'].'"');
            echo $row['content'];
        }
    } elseif ($method === 'POST' && $path === '/upload') {
        if (($_SERVER['HTTP_ORIGIN'] ?? '') !== $origin ||
            ($_SERVER['HTTP_X_LAB_EXERCISE'] ?? '') !== 'synthetic' ||
            ($_SERVER['CONTENT_TYPE'] ?? '') !== 'application/x-www-form-urlencoded' ||
            isset($_SERVER['HTTP_TRANSFER_ENCODING'])) {
            throw new Rejected(403);
        }
        $length = $_SERVER['CONTENT_LENGTH'] ?? '';
        if (!ctype_digit((string)$length) || (int)$length < 1 || (int)$length > 16384) {
            throw new Rejected(413);
        }
        $raw = file_get_contents('php://input', false, null, 0, 16385);
        if ($raw === false || strlen($raw) !== (int)$length) {
            throw new Rejected(400);
        }
        $fields = Store::form($raw);
        $keys = array_keys($fields);
        sort($keys);
        if ($keys !== ['content','filename'] || ($_SERVER['QUERY_STRING'] ?? '') !== '') {
            throw new Rejected(400);
        }
        echo json_encode(['id'=>$store->upload($identity, $fields['filename'], $fields['content'])], JSON_THROW_ON_ERROR);
    } else {
        throw new Rejected(405);
    }
} catch (Rejected $error) {
    http_response_code($error->status);
    echo '{"error":"request_rejected"}';
} catch (Throwable $error) {
    http_response_code(500);
    echo '{"error":"local_operation_failed"}';
}
