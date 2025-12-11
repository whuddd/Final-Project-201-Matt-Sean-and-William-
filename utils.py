import sqlite3
import os
import re


def connect_db(db_path: str = 'football_weather.db'):
    """Return a sqlite3 connection to the project database."""
    return sqlite3.connect(db_path)


def normalize_location(value):
    """Normalize location/stadium_city strings for safe joins.

    Lowercases, removes non-alphanumerics, collapses whitespace.
    Returns None for None-like inputs.
    """
    if value is None:
        return None
    s = str(value)
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def ensure_outputs_dir():
    ensure_dir('outputs')
    ensure_dir(os.path.join('outputs', 'figures'))
