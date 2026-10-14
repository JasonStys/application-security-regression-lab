<?php
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// variable: strict_types — line 135
// definition: Rejected — line 138
// symbol: __construct — line 141
// variable: status — line 141
// parameter: parent — line 143
// definition: Store — line 148
// variable: database — line 150
// symbol: __construct — line 153
// variable: dsn — line 153
// variable: database — line 155
// variable: dsn — line 155
// variable: this — line 155
// parameter: PDO — line 156
// variable: ATTR_ERRMODE — line 156
// parameter: PDO — line 157
// variable: ATTR_DEFAULT_FETCH_MODE — line 157
// variable: busy_timeout — line 159
// variable: this — line 159
// variable: foreign_keys — line 160
// variable: this — line 160
// variable: this — line 161
// variable: trusted_schema — line 161
// variable: this — line 162
// variable: version — line 162
// variable: version — line 163
// variable: this — line 164
// variable: this — line 166
// variable: this — line 167
// variable: error — line 168
// variable: this — line 169
// variable: error — line 170
// variable: version — line 172
// symbol: principal — line 178
// variable: header — line 178
// variable: fixtures — line 180
// variable: fixtures — line 185
// variable: header — line 185
// variable: fixtures — line 188
// variable: header — line 188
// symbol: form — line 192
// variable: raw — line 192
// variable: raw — line 194
// variable: fields — line 197
// variable: raw — line 198
// variable: fields — line 199
// variable: item — line 201
// variable: raw — line 201
// variable: item — line 202
// variable: pair — line 202
// variable: fields — line 203
// variable: pair — line 203
// variable: item — line 204
// variable: key — line 207
// variable: pair — line 207
// variable: pair — line 208
// variable: value — line 208
// variable: fields — line 209
// variable: key — line 209
// variable: value — line 209
// variable: fields — line 212
// variable: key — line 212
// variable: value — line 212
// variable: fields — line 214
// symbol: search — line 218
// variable: identity — line 218
// variable: query — line 218
// variable: query — line 220
// variable: literal — line 223
// variable: query — line 223
// variable: statement — line 224
// variable: tenant — line 224
// variable: this — line 224
// variable: identity — line 225
// variable: literal — line 225
// variable: statement — line 225
// variable: statement — line 226
// symbol: textUpload — line 230
// variable: content — line 230
// variable: filename — line 230
// variable: filename — line 232
// variable: filename — line 233
// variable: content — line 234
// variable: content — line 235
// symbol: upload — line 241
// variable: content — line 241
// variable: filename — line 241
// variable: identity — line 241
// variable: identity — line 243
// parameter: self — line 246
// variable: content — line 246
// variable: filename — line 246
// variable: this — line 247
// column: AS — line 249
// variable: quota — line 249
// variable: tenant — line 249
// variable: this — line 249
// variable: identity — line 250
// variable: quota — line 250
// variable: quota — line 251
// variable: used — line 251
// variable: content — line 252
// variable: used — line 252
// variable: id — line 255
// variable: statement — line 256
// variable: this — line 256
// variable: content — line 257
// variable: filename — line 257
// variable: id — line 257
// variable: identity — line 257
// variable: statement — line 257
// variable: this — line 258
// variable: id — line 259
// variable: error — line 260
// variable: this — line 261
// variable: error — line 262
// symbol: download — line 267
// variable: id — line 267
// variable: identity — line 267
// variable: id — line 269
// variable: id — line 272
// variable: statement — line 272
// variable: tenant — line 272
// variable: this — line 272
// variable: id — line 273
// variable: identity — line 273
// variable: statement — line 273
// variable: row — line 274
// variable: statement — line 274
// variable: row — line 275
// variable: row — line 278
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
