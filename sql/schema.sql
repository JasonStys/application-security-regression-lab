-- Jason Stys: synthetic tenant-scoped SQLite records and bounded text uploads, never executable files.
-- BEGIN CODE MAP (generated; python scripts/code_map.py)
-- SQL object: IF — line 14
-- column: id — line 15
-- column: tenant — line 16
-- column: body — line 17
-- SQL object: IF — line 19
-- column: id — line 20
-- column: tenant — line 21
-- column: filename — line 22
-- column: content — line 23
-- SQL object: IF — line 25
-- END CODE MAP
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    tenant TEXT NOT NULL,
    body TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS uploads (
    id TEXT PRIMARY KEY,
    tenant TEXT NOT NULL,
    filename TEXT NOT NULL,
    content TEXT NOT NULL
) STRICT;
CREATE INDEX IF NOT EXISTS uploads_by_tenant ON uploads(tenant,id);
INSERT OR IGNORE INTO notes VALUES ('alpha-note','alpha','Fictional Alpha maintenance');
INSERT OR IGNORE INTO notes VALUES ('beta-note','beta','Fictional Beta maintenance');
PRAGMA user_version=1;
