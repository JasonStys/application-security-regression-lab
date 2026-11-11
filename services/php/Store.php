<?php
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// variable: strict_types — line 143
// definition: Rejected — line 146
// symbol: __construct — line 149
// variable: status — line 149
// parameter: parent — line 151
// definition: Store — line 156
// variable: database — line 158
// definition: and — line 160
// symbol: failureCategory — line 161
// variable: error — line 161
// variable: error — line 163
// variable: code — line 164
// variable: error — line 164
// variable: code — line 165
// variable: error — line 167
// symbol: __construct — line 174
// variable: dsn — line 174
// variable: database — line 176
// variable: dsn — line 176
// variable: this — line 176
// parameter: PDO — line 177
// variable: ATTR_ERRMODE — line 177
// parameter: PDO — line 178
// variable: ATTR_DEFAULT_FETCH_MODE — line 178
// variable: busy_timeout — line 180
// variable: this — line 180
// variable: foreign_keys — line 181
// variable: this — line 181
// variable: this — line 182
// variable: trusted_schema — line 182
// variable: this — line 183
// variable: version — line 183
// variable: version — line 184
// variable: this — line 185
// variable: this — line 187
// variable: this — line 188
// variable: error — line 189
// variable: this — line 190
// variable: error — line 191
// variable: version — line 193
// symbol: principal — line 199
// variable: header — line 199
// variable: fixtures — line 201
// variable: fixtures — line 206
// variable: header — line 206
// variable: fixtures — line 209
// variable: header — line 209
// symbol: form — line 213
// variable: raw — line 213
// variable: raw — line 215
// variable: fields — line 218
// variable: raw — line 219
// variable: fields — line 220
// variable: item — line 222
// variable: raw — line 222
// variable: item — line 223
// variable: pair — line 223
// variable: fields — line 224
// variable: pair — line 224
// variable: item — line 225
// variable: key — line 228
// variable: pair — line 228
// variable: pair — line 229
// variable: value — line 229
// variable: fields — line 230
// variable: key — line 230
// variable: value — line 230
// variable: fields — line 233
// variable: key — line 233
// variable: value — line 233
// variable: fields — line 235
// symbol: search — line 239
// variable: identity — line 239
// variable: query — line 239
// variable: query — line 241
// variable: literal — line 244
// variable: query — line 244
// variable: statement — line 245
// variable: tenant — line 245
// variable: this — line 245
// variable: identity — line 246
// variable: literal — line 246
// variable: statement — line 246
// variable: statement — line 247
// symbol: textUpload — line 251
// variable: content — line 251
// variable: filename — line 251
// variable: filename — line 253
// variable: filename — line 254
// variable: content — line 255
// variable: content — line 256
// symbol: upload — line 262
// variable: content — line 262
// variable: filename — line 262
// variable: identity — line 262
// variable: identity — line 264
// parameter: self — line 267
// variable: content — line 267
// variable: filename — line 267
// variable: this — line 268
// column: AS — line 270
// variable: quota — line 270
// variable: tenant — line 270
// variable: this — line 270
// variable: identity — line 271
// variable: quota — line 271
// variable: quota — line 272
// variable: used — line 272
// variable: content — line 273
// variable: used — line 273
// variable: id — line 276
// variable: statement — line 277
// variable: this — line 277
// variable: content — line 278
// variable: filename — line 278
// variable: id — line 278
// variable: identity — line 278
// variable: statement — line 278
// variable: this — line 279
// variable: id — line 280
// variable: error — line 281
// variable: this — line 282
// variable: error — line 283
// symbol: download — line 288
// variable: id — line 288
// variable: identity — line 288
// variable: id — line 290
// variable: id — line 293
// variable: statement — line 293
// variable: tenant — line 293
// variable: this — line 293
// variable: id — line 294
// variable: identity — line 294
// variable: statement — line 294
// variable: row — line 295
// variable: statement — line 295
// variable: row — line 296
// variable: row — line 299
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
            $code = $error->errorInfo[1] ?? 0;
            return 'database_'.(is_int($code) && $code >= 0 && $code <= 65535 ? $code : 0);
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
