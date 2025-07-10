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

    def to_json(self):
        return {
            'selected': self.selected,
            'comment': self.comment,
            'marks': self.marks,
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

    def __init__(self, dbpath: Path):
        self.dbpath = dbpath
        self.conn = sqlite3.connect(
            self.dbpath,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute('''
                          CREATE TABLE IF NOT EXISTS annotations
                          (
                              rowid INTEGER PRIMARY KEY,
                              annotation TEXT NOT NULL,
                              last_update_utc TIMESTAMP NOT NULL
                          )
                          ''')
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

    def export(self):
        with open(self.dbpath.parent / f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db.jsonl',
                  'w', encoding='utf8') as out:
            for rowid, annotation in self.conn.execute('SELECT rowid, annotation FROM annotations'):
                d = json.loads(annotation)
                d['row'] = rowid
                out.write(json.dumps(d) + '\n')


    def close(self):
        self.conn.close()
