"""Small SQLite repository. Each operation opens a short-lived connection."""
import os
import sqlite3
from pathlib import Path


def connect():
    path = Path(os.environ.get('DATABASE_PATH', 'data/growth.db'))
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


def init():
    with connect() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS publications(id TEXT PRIMARY KEY, draft_id TEXT NOT NULL UNIQUE, x_id TEXT NOT NULL UNIQUE, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS measurements(id TEXT PRIMARY KEY, publication_id TEXT NOT NULL REFERENCES publications(id), measured_at TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS measurements_publication ON measurements(publication_id,measured_at);
        CREATE TABLE IF NOT EXISTS manual_posts(id TEXT PRIMARY KEY, handle TEXT NOT NULL, created_at TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS manual_posts_handle ON manual_posts(handle,created_at);
        CREATE TABLE IF NOT EXISTS x_accounts(handle TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS x_posts(id TEXT NOT NULL, handle TEXT NOT NULL, created_at TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(handle,id));
        CREATE TABLE IF NOT EXISTS x_control(id INTEGER PRIMARY KEY CHECK(id=1), next_fetch_at REAL NOT NULL DEFAULT 0, blocked_until REAL NOT NULL DEFAULT 0);
        INSERT OR IGNORE INTO x_control(id) VALUES(1);
        CREATE TABLE IF NOT EXISTS x_requests(id INTEGER PRIMARY KEY, attempted_at REAL NOT NULL);
        CREATE INDEX IF NOT EXISTS x_posts_handle ON x_posts(handle,created_at);
        CREATE TABLE IF NOT EXISTS accounts(handle TEXT PRIMARY KEY, enabled INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS posts(id TEXT PRIMARY KEY, handle TEXT NOT NULL, text TEXT NOT NULL,
          created_at TEXT NOT NULL, likes INTEGER NOT NULL, reposts INTEGER NOT NULL, replies INTEGER NOT NULL,
          provenance TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS analyses(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS drafts(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        ''')
