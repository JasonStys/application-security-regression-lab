<?php
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// variable: strict_types — line 79
// variable: charset — line 88
// variable: _SERVER — line 90
// variable: port — line 90
// variable: origin — line 91
// variable: port — line 91
// variable: _SERVER — line 92
// variable: port — line 92
// variable: _SERVER — line 93
// variable: origin — line 93
// variable: _SERVER — line 94
// variable: _SERVER — line 97
// variable: method — line 97
// variable: _SERVER — line 98
// variable: path — line 98
// variable: method — line 99
// variable: path — line 99
// variable: nonce — line 100
// variable: nonce — line 101
// variable: nonce — line 102
// variable: path — line 109
// variable: _SERVER — line 112
// variable: identity — line 112
// variable: database — line 113
// variable: database — line 114
// variable: database — line 117
// variable: store — line 117
// variable: method — line 118
// variable: _SERVER — line 119
// variable: fields — line 119
// variable: expected — line 120
// variable: path — line 120
// variable: expected — line 121
// variable: fields — line 121
// variable: path — line 121
// variable: path — line 124
// variable: fields — line 125
// variable: identity — line 125
// variable: store — line 125
// variable: fields — line 127
// variable: identity — line 127
// variable: row — line 127
// variable: store — line 127
// variable: charset — line 128
// variable: filename — line 129
// variable: row — line 129
// variable: row — line 130
// variable: method — line 132
// variable: path — line 132
// variable: _SERVER — line 133
// variable: origin — line 133
// variable: _SERVER — line 134
// variable: _SERVER — line 135
// variable: _SERVER — line 136
// variable: _SERVER — line 139
// variable: length — line 139
// variable: length — line 140
// variable: raw — line 143
// variable: length — line 144
// variable: raw — line 144
// variable: fields — line 147
// variable: raw — line 147
// variable: fields — line 148
// variable: keys — line 148
// variable: keys — line 149
// variable: _SERVER — line 150
// variable: keys — line 150
// variable: fields — line 153
// variable: identity — line 153
// variable: store — line 153
// variable: error — line 157
// variable: error — line 158
// variable: error — line 160
// variable: error — line 162
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
        $nonce = getenv('ASRL_OWNED_NONCE');
        if (is_string($nonce) && preg_match('/\A[a-f0-9]{64}\z/D', $nonce) === 1) {
            header('X-Lab-Owned-Nonce: '.$nonce);
        }
        header('X-Lab-Runtime: '.PHP_VERSION);
        header('X-Lab-Sqlite: '.(in_array('sqlite', PDO::getAvailableDrivers(), true) ? 'available' : 'unavailable'));
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
    header('X-Lab-Error-Category: '.Store::failureCategory($error));
    echo '{"error":"local_operation_failed"}';
}
