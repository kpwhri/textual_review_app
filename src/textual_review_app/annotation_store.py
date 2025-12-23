import json
from datetime import datetime, timezone
import sqlite3
from pathlib import Path


class Annotation:

    def __init__(self, rowid: int, data: str = None):
        if data is None:
            data = {}
        else:
            data = json.loads(data)
        self.rowid = rowid
        self.selected = data.get('selected', list())
        self.comment = data.get('comment', '')
        self.marks = data.get('marks', list())
        self.flagged = bool(data.get('flagged', False))

    def to_json(self):
        return {
            'selected': self.selected,
            'comment': self.comment,
            'marks': self.marks,
            'flagged': self.flagged,
        }

    def to_json_str(self):
        return json.dumps(self.to_json())

    def add_mark(self, start, end, selection, kind):
        self.marks.append({
            'start': start,
            'end': end,
            'kind': kind,
            'selection': selection,
        })


class AnnotationStore:

    def __init__(self, dbpath: Path, user: str | None = None):
        self.dbpath = dbpath
        self.conn = sqlite3.connect(
            self.dbpath,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.conn.row_factory = sqlite3.Row
        # WAL and schema versioning
        try:
            self.conn.execute('PRAGMA journal_mode=WAL;')
        except Exception:
            pass
        self.conn.execute('PRAGMA user_version=1;')
        self._create_table()
        self.user = user or 'anonymous'

    def _create_table(self):
        self.conn.execute('''
                          CREATE TABLE IF NOT EXISTS annotations
                          (
                              rowid INTEGER PRIMARY KEY,
                              annotation TEXT NOT NULL,
                              last_update_utc TIMESTAMP NOT NULL
                          )
                          ''')
        # index on rowid (redundant with PK but explicit per requirements)
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_annotations_rowid ON annotations(rowid);')
        self.conn.commit()

    def save(self, rowid, annotation: Annotation):
        self.conn.execute('''
                          INSERT INTO annotations (rowid, annotation, last_update_utc)
                          VALUES (?, ?, ?) ON CONFLICT(rowid) DO
                          UPDATE SET
                              annotation = excluded.annotation,
                              last_update_utc = excluded.last_update_utc
                          ''', (rowid, annotation.to_json_str(), datetime.now(timezone.utc)))
        self.conn.commit()

    def get(self, rowid):
        cur = self.conn.execute('''
                                SELECT rowid, annotation
                                FROM annotations
                                WHERE rowid = ?
                                ''', (rowid,))
        if row := cur.fetchone():
            return Annotation(rowid, row['annotation'])
        return Annotation(rowid)

    def exists(self, rowid: int) -> bool:
        """Return True if an annotation record exists for the given rowid.

        This does not infer from default objects; it checks the database presence.
        """
        cur = self.conn.execute('SELECT 1 FROM annotations WHERE rowid = ? LIMIT 1', (rowid,))
        return cur.fetchone() is not None

    def recent_reviewed_ids(self, n=None):
        """Yield rowids that have been reviewed (persisted in the DB)."""
        limit = f'LIMIT {n}' if n else ''
        cur = self.conn.execute(f'SELECT rowid FROM annotations ORDER BY last_update_utc DESC {limit}')
        return sorted(row['rowid'] for row in cur)

    def export(self):
        with open(self.dbpath.parent / f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db.jsonl',
                  'w', encoding='utf8') as out:
            for rowid, annotation in self.conn.execute('SELECT rowid, annotation FROM annotations'):
                d = json.loads(annotation)
                d['row'] = rowid
                d['user'] = self.user
                out.write(json.dumps(d) + '\n')


    def close(self):
        self.conn.close()
