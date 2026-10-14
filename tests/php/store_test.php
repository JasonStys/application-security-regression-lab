<?php
// BEGIN CODE MAP (generated; python scripts/code_map.py)
// symbol: tests — line 102
// variable: strict_types — line 103
// variable: cases — line 105
// symbol: checkCase — line 108
// variable: condition — line 108
// variable: id — line 108
// variable: cases — line 110
// variable: condition — line 111
// variable: id — line 112
// variable: cases — line 114
// variable: id — line 114
// symbol: denied — line 118
// variable: id — line 118
// variable: operation — line 118
// variable: status — line 118
// variable: caught — line 120
// variable: caught — line 121
// variable: error — line 121
// variable: operation — line 121
// variable: status — line 121
// variable: caught — line 122
// variable: id — line 122
// variable: store — line 125
// variable: alpha — line 126
// variable: beta — line 127
// variable: viewer — line 128
// variable: alpha — line 129
// variable: store — line 129
// variable: alpha — line 130
// variable: store — line 130
// variable: alpha — line 131
// variable: store — line 131
// variable: index — line 132
// variable: query — line 132
// variable: alpha — line 133
// variable: index — line 133
// variable: query — line 133
// variable: store — line 133
// variable: alpha — line 135
// variable: store — line 135
// variable: index — line 138
// variable: name — line 138
// variable: index — line 139
// variable: name — line 139
// variable: content — line 141
// variable: index — line 141
// variable: content — line 142
// variable: index — line 142
// variable: store — line 144
// variable: viewer — line 144
// variable: alpha — line 145
// variable: id — line 145
// variable: store — line 145
// variable: alpha — line 146
// variable: id — line 146
// variable: store — line 146
// variable: beta — line 147
// variable: id — line 147
// variable: store — line 147
// variable: alpha — line 148
// variable: store — line 148
// variable: alpha — line 149
// variable: store — line 149
// variable: alpha — line 150
// variable: index — line 150
// variable: store — line 150
// variable: alpha — line 151
// variable: store — line 151
// variable: alpha — line 152
// variable: id — line 152
// variable: store — line 152
// variable: beta — line 153
// variable: index — line 153
// variable: store — line 153
// variable: beta — line 154
// variable: store — line 154
// variable: index — line 155
// variable: raw — line 155
// variable: x — line 155
// variable: index — line 156
// variable: raw — line 156
// variable: x — line 158
// variable: comparison — line 161
// SQL object: notes — line 162
// column: body — line 162
// variable: comparison — line 162
// variable: attack — line 163
// variable: attack — line 164
// variable: body — line 164
// variable: comparison — line 164
// variable: unsafe — line 164
// variable: alpha — line 165
// variable: attack — line 165
// variable: store — line 165
// variable: unsafe — line 165
// variable: unsafeNameAccepts — line 166
// variable: unsafeNameAccepts — line 167
// variable: cases — line 169
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
echo json_encode(['component'=>'php','passed'=>count($cases),'mutants_killed'=>2,'cases'=>$cases], JSON_THROW_ON_ERROR).PHP_EOL;
