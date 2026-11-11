<?php
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// symbol: tests — line 112
// variable: strict_types — line 113
// variable: cases — line 115
// symbol: checkCase — line 118
// variable: condition — line 118
// variable: id — line 118
// variable: cases — line 120
// variable: condition — line 121
// variable: id — line 122
// variable: cases — line 124
// variable: id — line 124
// symbol: denied — line 128
// variable: id — line 128
// variable: operation — line 128
// variable: status — line 128
// variable: caught — line 130
// variable: caught — line 131
// variable: error — line 131
// variable: operation — line 131
// variable: status — line 131
// variable: caught — line 132
// variable: id — line 132
// variable: store — line 135
// variable: alpha — line 136
// variable: beta — line 137
// variable: viewer — line 138
// variable: alpha — line 139
// variable: store — line 139
// variable: alpha — line 140
// variable: store — line 140
// variable: alpha — line 141
// variable: store — line 141
// variable: index — line 142
// variable: query — line 142
// variable: alpha — line 143
// variable: index — line 143
// variable: query — line 143
// variable: store — line 143
// variable: alpha — line 145
// variable: store — line 145
// variable: index — line 148
// variable: name — line 148
// variable: index — line 149
// variable: name — line 149
// variable: content — line 151
// variable: index — line 151
// variable: content — line 152
// variable: index — line 152
// variable: store — line 154
// variable: viewer — line 154
// variable: alpha — line 155
// variable: id — line 155
// variable: store — line 155
// variable: alpha — line 156
// variable: id — line 156
// variable: store — line 156
// variable: beta — line 157
// variable: id — line 157
// variable: store — line 157
// variable: alpha — line 158
// variable: store — line 158
// variable: alpha — line 159
// variable: store — line 159
// variable: alpha — line 160
// variable: index — line 160
// variable: store — line 160
// variable: alpha — line 161
// variable: store — line 161
// variable: alpha — line 162
// variable: id — line 162
// variable: store — line 162
// variable: beta — line 163
// variable: index — line 163
// variable: store — line 163
// variable: beta — line 164
// variable: store — line 164
// variable: index — line 165
// variable: raw — line 165
// variable: x — line 165
// variable: index — line 166
// variable: raw — line 166
// variable: x — line 168
// variable: comparison — line 171
// SQL object: notes — line 172
// column: body — line 172
// variable: comparison — line 172
// variable: attack — line 173
// variable: attack — line 174
// variable: body — line 174
// variable: comparison — line 174
// variable: unsafe — line 174
// variable: alpha — line 175
// variable: attack — line 175
// variable: store — line 175
// variable: unsafe — line 175
// variable: unsafeNameAccepts — line 176
// variable: unsafeNameAccepts — line 177
// variable: comparison — line 182
// variable: error — line 184
// variable: error — line 185
// variable: comparison — line 187
// variable: query_only — line 187
// SQL object: private_write_refused — line 189
// column: value — line 189
// variable: comparison — line 189
// variable: error — line 191
// variable: error — line 192
// variable: cases — line 195
// END CODE MAP
/** Jason Stys: real in-memory PDO tests and deliberately incorrect test-only SQL/name predicates, never served. */
declare(strict_types=1);
require_once __DIR__.'/../../services/php/Store.php';
$cases = [];

/** Evaluate a condition before recording its case; failure stops the native process with a fixed ID. */
function checkCase(string $id, bool $condition): void
{
    global $cases;
    if (!$condition) {
        throw new RuntimeException($id);
    }
    $cases[] = $id;
}

/** Assert an exact rejection category, not merely any unrelated failure. */
function denied(string $id, int $status, callable $operation): void
{
    $caught = false;
    try { $operation(); } catch (Rejected $error) { $caught = $error->status === $status; }
    checkCase($id, $caught);
}

$store = new Store('sqlite::memory:');
$alpha = Store::principal('Bearer fixture-alpha-owner');
$beta = Store::principal('Bearer fixture-beta-owner');
$viewer = Store::principal('Bearer fixture-alpha-viewer');
checkCase('P-01-own-search', count($store->search($alpha, '')) === 1);
checkCase('P-02-tenant-filter', $store->search($alpha, 'Beta') === []);
checkCase('P-03-query-literal', $store->search($alpha, "' OR 1=1 --") === []);
foreach (['%', '_', '\\', "x\0", str_repeat('x', 100)] as $index=>$query) {
    checkCase('P-04-literal-'.$index, $store->search($alpha, $query) === []);
}
denied('P-05-size-query', 400, fn() => $store->search($alpha, str_repeat('x', 101)));
denied('P-06-unknown-token', 401, fn() => Store::principal('claimed-admin'));
denied('P-07-null-token', 401, fn() => Store::principal(null));
foreach (['../a.txt','a.php','a.php.txt','.a.txt','a/b.txt','a\\b.txt','CON.txt','lpt9.txt','a.txt%00.php','a.txt ',str_repeat('a',49).'.txt'] as $index=>$name) {
    denied('P-08-name-'.$index, 400, fn() => Store::textUpload($name, 'hello'));
}
foreach (['', "\0", "\x01", "\xff", str_repeat('x',4097)] as $index=>$content) {
    denied('P-09-content-'.$index, 400, fn() => Store::textUpload('a.txt', $content));
}
denied('P-10-viewer-upload', 403, fn() => $store->upload($viewer, 'a.txt', 'hello'));
$id = $store->upload($alpha, 'report.txt', "<script>ignored as text</script>\n✓");
checkCase('P-11-download-literal', $store->download($alpha, $id)['content'] === "<script>ignored as text</script>\n✓");
denied('P-12-cross-download', 404, fn() => $store->download($beta, $id));
denied('P-13-missing-download', 404, fn() => $store->download($alpha, str_repeat('0',16)));
denied('P-14-bad-download', 400, fn() => $store->download($alpha, '../x'));
for ($index=0; $index<3; $index++) { $store->upload($alpha, 'a.txt', str_repeat('x',4096)); }
denied('P-15-byte-quota', 429, fn() => $store->upload($alpha, 'a.txt', str_repeat('x',4096)));
checkCase('P-16-rollback-preserves', $store->download($alpha, $id)['filename'] === 'report.txt');
for ($index=0; $index<8; $index++) { $store->upload($beta, 'a.txt', 'x'); }
denied('P-17-count-quota', 429, fn() => $store->upload($beta, 'a.txt', 'x'));
foreach (['x=a&x=b','x','x=%FF','x=%','x=%GG','x=é',str_repeat('x',16385)] as $index=>$raw) {
    denied('P-18-form-'.$index, 400, fn() => Store::form($raw));
}
checkCase('P-19-decode-once', Store::form('x=%253C+%E2%9C%93')['x'] === '%3C ✓');
checkCase('P-20-empty-form', Store::form('') === []);
// A real deliberately unsafe query operates only on an isolated synthetic in-memory comparison database.
$comparison = new PDO('sqlite::memory:');
$comparison->exec("CREATE TABLE notes(body TEXT); INSERT INTO notes VALUES('alpha'),('beta')");
$attack = "' OR 1=1 --";
$unsafe = $comparison->query("SELECT body FROM notes WHERE body='".$attack."'")->fetchAll();
checkCase('M-P-SQL-killed', count($unsafe) === 2 && $store->search($alpha, $attack) === []);
$unsafeNameAccepts = str_ends_with('../a.txt', '.txt');
checkCase('M-P-path-witness', $unsafeNameAccepts);
denied('M-P-path-killed',400,fn() => Store::textUpload('../a.txt','x'));

// Real driver failures expose only native numeric classes, never the private SQL or error body.
try {
    $comparison->query('SELECT * FROM private_missing_table');
    throw new RuntimeException('expected actual SQLite missing-table failure');
} catch (PDOException $error) {
    checkCase('P-21-private-error-missing-table', Store::failureCategory($error) === 'database_1');
}
$comparison->exec('PRAGMA query_only=ON');
try {
    $comparison->exec('CREATE TABLE private_write_refused(value TEXT)');
    throw new RuntimeException('expected actual SQLite read-only failure');
} catch (PDOException $error) {
    checkCase('P-22-private-error-readonly', Store::failureCategory($error) === 'database_8');
}
checkCase('P-23-private-error-no-message', Store::failureCategory(new RuntimeException('private SQL/path/body must never appear')) === 'operation');
echo json_encode(['component'=>'php','passed'=>count($cases),'mutants_killed'=>2,'cases'=>$cases], JSON_THROW_ON_ERROR).PHP_EOL;
