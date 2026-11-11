<?php
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// variable: strict_types — line 146
// definition: Rejected — line 149
// symbol: __construct — line 152
// variable: status — line 152
// parameter: parent — line 154
// definition: Store — line 159
// variable: database — line 161
// definition: and — line 163
// symbol: failureCategory — line 164
// variable: error — line 164
// variable: error — line 166
// variable: code — line 170
// variable: error — line 170
// variable: code — line 171
// variable: valid — line 171
// variable: code — line 172
// variable: valid — line 172
// variable: error — line 174
// symbol: __construct — line 181
// variable: dsn — line 181
// variable: database — line 183
// variable: dsn — line 183
// variable: this — line 183
// parameter: PDO — line 184
// variable: ATTR_ERRMODE — line 184
// parameter: PDO — line 185
// variable: ATTR_DEFAULT_FETCH_MODE — line 185
// variable: busy_timeout — line 187
// variable: this — line 187
// variable: foreign_keys — line 188
// variable: this — line 188
// variable: this — line 189
// variable: trusted_schema — line 189
// variable: this — line 190
// variable: version — line 190
// variable: version — line 191
// variable: this — line 192
// variable: this — line 194
// variable: this — line 195
// variable: error — line 196
// variable: this — line 197
// variable: error — line 198
// variable: version — line 200
// symbol: principal — line 206
// variable: header — line 206
// variable: fixtures — line 208
// variable: fixtures — line 213
// variable: header — line 213
// variable: fixtures — line 216
// variable: header — line 216
// symbol: form — line 220
// variable: raw — line 220
// variable: raw — line 222
// variable: fields — line 225
// variable: raw — line 226
// variable: fields — line 227
// variable: item — line 229
// variable: raw — line 229
// variable: item — line 230
// variable: pair — line 230
// variable: fields — line 231
// variable: pair — line 231
// variable: item — line 232
// variable: key — line 235
// variable: pair — line 235
// variable: pair — line 236
// variable: value — line 236
// variable: fields — line 237
// variable: key — line 237
// variable: value — line 237
// variable: fields — line 240
// variable: key — line 240
// variable: value — line 240
// variable: fields — line 242
// symbol: search — line 246
// variable: identity — line 246
// variable: query — line 246
// variable: query — line 248
// variable: literal — line 251
// variable: query — line 251
// variable: statement — line 252
// variable: tenant — line 252
// variable: this — line 252
// variable: identity — line 253
// variable: literal — line 253
// variable: statement — line 253
// variable: statement — line 254
// symbol: textUpload — line 258
// variable: content — line 258
// variable: filename — line 258
// variable: filename — line 260
// variable: filename — line 261
// variable: content — line 262
// variable: content — line 263
// symbol: upload — line 269
// variable: content — line 269
// variable: filename — line 269
// variable: identity — line 269
// variable: identity — line 271
// parameter: self — line 274
// variable: content — line 274
// variable: filename — line 274
// variable: this — line 275
// column: AS — line 277
// variable: quota — line 277
// variable: tenant — line 277
// variable: this — line 277
// variable: identity — line 278
// variable: quota — line 278
// variable: quota — line 279
// variable: used — line 279
// variable: content — line 280
// variable: used — line 280
// variable: id — line 283
// variable: statement — line 284
// variable: this — line 284
// variable: content — line 285
// variable: filename — line 285
// variable: id — line 285
// variable: identity — line 285
// variable: statement — line 285
// variable: this — line 286
// variable: id — line 287
// variable: error — line 288
// variable: this — line 289
// variable: error — line 290
// symbol: download — line 295
// variable: id — line 295
// variable: identity — line 295
// variable: id — line 297
// variable: id — line 300
// variable: statement — line 300
// variable: tenant — line 300
// variable: this — line 300
// variable: id — line 301
// variable: identity — line 301
// variable: statement — line 301
// variable: row — line 302
// variable: statement — line 302
// variable: row — line 303
// variable: row — line 306
// END CODE MAP
/** Jason Stys: native prepared SQLite queries, authoritative tenant scope and bounded nonexecuting text uploads. */
declare(strict_types=1);

/** Fixed safe boundary status. Input strings, SQL, paths and credentials never become exception text. */
final class Rejected extends RuntimeException
{
    /** Create a constant error category with HTTP status held separately. */
    public function __construct(public readonly int $status)
    {
        parent::__construct('request_rejected');
    }
}

/** Corrected store: every externally influenced value is a bound parameter, never an SQL identifier. */
final class Store
{
    private PDO $database;

    /** Return only a fixed operation class and bounded native SQLite code; never SQL, paths or exception text. */
    public static function failureCategory(Throwable $error): string
    {
        if ($error instanceof PDOException) {
            if (!in_array('sqlite', PDO::getAvailableDrivers(), true)) {
                return 'driver_unavailable';
            }
            $code = $error->errorInfo[1] ?? 0;
            $valid = is_int($code) || is_string($code) && ctype_digit($code);
            return 'database_'.($valid && (int)$code >= 0 && (int)$code <= 65535 ? (int)$code : 0);
        }
        if ($error instanceof Random\RandomException) {
            return 'entropy';
        }
        return 'operation';
    }

    /** Open an explicit trusted fixture DSN; initialize version 0 transactionally, reject unknown versions. */
    public function __construct(string $dsn)
    {
        $this->database = new PDO($dsn, null, null, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
        $this->database->exec('PRAGMA busy_timeout=3000');
        $this->database->exec('PRAGMA foreign_keys=ON');
        $this->database->exec('PRAGMA trusted_schema=OFF');
        $version = (int)$this->database->query('PRAGMA user_version')->fetchColumn();
        if ($version === 0) {
            $this->database->beginTransaction();
            try {
                $this->database->exec((string)file_get_contents(__DIR__.'/../../sql/schema.sql'));
                $this->database->commit();
            } catch (Throwable $error) {
                $this->database->rollBack();
                throw $error;
            }
        } elseif ($version !== 1) {
            throw new Rejected(409);
        }
    }

    /** Resolve only a closed public fixture token; client tenant/role parameters are never identity. */
    public static function principal(?string $header): array
    {
        $fixtures = [
            'Bearer fixture-alpha-owner' => ['tenant'=>'alpha','owner'=>true],
            'Bearer fixture-alpha-viewer' => ['tenant'=>'alpha','owner'=>false],
            'Bearer fixture-beta-owner' => ['tenant'=>'beta','owner'=>true]
        ];
        if (!isset($fixtures[$header ?? ''])) {
            throw new Rejected(401);
        }
        return $fixtures[$header];
    }

    /** Decode a bounded flat form once as UTF8, rejecting malformed percent encodings and duplicate keys. */
    public static function form(string $raw): array
    {
        if (strlen($raw) > 16384 || preg_match('/[^\x20-\x7e]/', $raw) === 1) {
            throw new Rejected(400);
        }
        $fields = [];
        if ($raw === '') {
            return $fields;
        }
        foreach (explode('&', $raw) as $item) {
            $pair = explode('=', $item, 2);
            if (count($pair) !== 2 || count($fields) >= 8 ||
                preg_match('/%(?![a-fA-F0-9]{2})/', $item) === 1) {
                throw new Rejected(400);
            }
            $key = urldecode($pair[0]);
            $value = urldecode($pair[1]);
            if (array_key_exists($key, $fields) || preg_match('//u', $key.$value) !== 1) {
                throw new Rejected(400);
            }
            $fields[$key] = $value;
        }
        return $fields;
    }

    /** Query same-tenant literal text; LIKE wildcard characters and escape characters are treated as data. */
    public function search(array $identity, string $query): array
    {
        if (strlen($query) > 100 || preg_match('//u', $query) !== 1) {
            throw new Rejected(400);
        }
        $literal = str_replace(['\\','%','_'], ['\\\\','\\%','\\_'], $query);
        $statement = $this->database->prepare("SELECT id,body FROM notes WHERE tenant=? AND body LIKE ? ESCAPE '\\' ORDER BY id LIMIT 10");
        $statement->execute([$identity['tenant'], '%'.$literal.'%']);
        return $statement->fetchAll();
    }

    /** Validate only portable .txt logical names and bounded UTF8 text; no archives, scripts or disk paths. */
    public static function textUpload(string $filename, string $content): void
    {
        if (!preg_match('/\A[a-zA-Z][a-zA-Z0-9_-]{0,47}\.txt\z/', $filename) ||
            preg_match('/\A(?:con|prn|aux|nul|com[1-9]|lpt[1-9])\.txt\z/i', $filename) ||
            strlen($content) < 1 || strlen($content) > 4096 || preg_match('//u', $content) !== 1 ||
            preg_match('/[\x00-\x08\x0b\x0c\x0e-\x1f]/', $content)) {
            throw new Rejected(400);
        }
    }

    /** Store a validated text upload atomically under authoritative tenant, returning an opaque ID, not a path. */
    public function upload(array $identity, string $filename, string $content): string
    {
        if (!$identity['owner']) {
            throw new Rejected(403);
        }
        self::textUpload($filename, $content);
        $this->database->exec('BEGIN IMMEDIATE');
        try {
            $quota = $this->database->prepare('SELECT count(*),coalesce(sum(length(cast(content AS BLOB))),0) FROM uploads WHERE tenant=?');
            $quota->execute([$identity['tenant']]);
            $used = $quota->fetch(PDO::FETCH_NUM);
            if ((int)$used[0] >= 8 || (int)$used[1] + strlen($content) > 16384) {
                throw new Rejected(429);
            }
            $id = bin2hex(random_bytes(8));
            $statement = $this->database->prepare('INSERT INTO uploads VALUES(?,?,?,?)');
            $statement->execute([$id, $identity['tenant'], $filename, $content]);
            $this->database->exec('COMMIT');
            return $id;
        } catch (Throwable $error) {
            $this->database->exec('ROLLBACK');
            throw $error;
        }
    }

    /** Return only a same-tenant upload; missing and cross-tenant IDs have the same 404 status. */
    public function download(array $identity, string $id): array
    {
        if (!preg_match('/\A[a-f0-9]{16}\z/', $id)) {
            throw new Rejected(400);
        }
        $statement = $this->database->prepare('SELECT filename,content FROM uploads WHERE tenant=? AND id=?');
        $statement->execute([$identity['tenant'], $id]);
        $row = $statement->fetch();
        if ($row === false) {
            throw new Rejected(404);
        }
        return $row;
    }
}
