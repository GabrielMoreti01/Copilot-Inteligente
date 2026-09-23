import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class Store:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        (self.directory / 'media').mkdir(exist_ok=True)
        self.path = self.directory / 'copiloto.sqlite3'
        with self.transaction() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS trips(id TEXT PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, trip_id TEXT NOT NULL REFERENCES trips(id), data TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS events_trip ON events(trip_id);
            ''')

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.execute('PRAGMA foreign_keys=ON')
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def trip(db, trip_id):
        row = db.execute('SELECT data FROM trips WHERE id=?', (trip_id,)).fetchone()
        return json.loads(row[0]) if row else None

    @staticmethod
    def events(db, trip_id):
        return sorted([json.loads(row[0]) for row in db.execute('SELECT data FROM events WHERE trip_id=?', (trip_id,))], key=lambda e: e['horario'])

    @staticmethod
    def save_trip(db, trip):
        db.execute('INSERT INTO trips VALUES (?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data', (trip['id'], json.dumps(trip, ensure_ascii=False)))
