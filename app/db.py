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
        CREATE TABLE IF NOT EXISTS accounts(handle TEXT PRIMARY KEY, enabled INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS posts(id TEXT PRIMARY KEY, handle TEXT NOT NULL, text TEXT NOT NULL,
          created_at TEXT NOT NULL, likes INTEGER NOT NULL, reposts INTEGER NOT NULL, replies INTEGER NOT NULL,
          provenance TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS analyses(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS drafts(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        ''')
