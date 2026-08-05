"""Database compatibility layer for SQLite and PostgreSQL.

Usage:
    from api.db_compat import get_placeholder, get_cursor, dict_row

The placeholder() function returns '?' for SQLite and '%s' for PostgreSQL.
All raw SQL should use this instead of hardcoding '?'.

The get_cursor() function returns a cursor configured with the right row
factory (sqlite3.Row for SQLite, RealDictCursor for PostgreSQL).
"""

import os
import logging

logger = logging.getLogger("resume-analyzer")

_db_type = None


def get_db_type():
    """Detect database type from environment. Returns 'sqlite' or 'postgresql'."""
    global _db_type
    if _db_type is not None:
        return _db_type

    database_url = os.getenv("DATABASE_URL", "")
    db_file = os.getenv("DB_FILE", "")

    if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
        _db_type = "postgresql"
    elif database_url.startswith("sqlite://") or db_file.endswith(".db") or not database_url:
        _db_type = "sqlite"
    else:
        _db_type = "sqlite"

    logger.info(f"Database type: {_db_type}")
    return _db_type


def placeholder():
    """Return the parameter placeholder for the current database driver."""
    return "%s" if get_db_type() == "postgresql" else "?"


def ph():
    """Shorthand alias for placeholder()."""
    return placeholder()


def get_engine_url():
    """Build SQLAlchemy engine URL from environment."""
    database_url = os.getenv("DATABASE_URL", "")

    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    db_file = os.getenv("DB_FILE") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "cv.db"
    )
    return f"sqlite:///{db_file}"


def get_connect_args():
    """Return database-specific connect_args for SQLAlchemy."""
    if get_db_type() == "sqlite":
        return {"check_same_thread": False}
    return {}


def configure_connection(dbapi_connection):
    """Configure a raw DBAPI connection. Called on each new connection."""
    if get_db_type() == "sqlite":
        import sqlite3
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
        dbapi_connection.row_factory = sqlite3.Row


def get_row_factory():
    """Return the cursor_factory for PostgreSQL, or None for SQLite."""
    if get_db_type() == "postgresql":
        import psycopg2.extras
        return psycopg2.extras.RealDictCursor
    return None


def dict_from_row(row):
    """Convert a database row to dict, handling both sqlite3.Row and RealDictCursor."""
    if row is None:
        return None
    if isinstance(row, dict):
        return dict(row)
    try:
        return dict(row)
    except (TypeError, ValueError):
        return {desc[0]: val for desc, val in zip(row.cursor_description, row) if desc} if hasattr(row, 'cursor_description') else list(row)


def list_placeholders(count):
    """Return a comma-separated list of placeholders for COUNT parameters."""
    p = placeholder()
    return ", ".join([p] * count)


def now_sql():
    """Return SQL for current timestamp."""
    return "CURRENT_TIMESTAMP"


def datetime_offset_sql(minutes):
    """Return SQL for current timestamp minus N minutes."""
    if get_db_type() == "postgresql":
        return f"NOW() - INTERVAL '{minutes} minutes'"
    return f"datetime('now', '-{minutes} minutes')"


def date_trunc_sql(column):
    """Return SQL to extract date from timestamp column."""
    if get_db_type() == "postgresql":
        return f"({column})::date"
    return f"DATE({column})"


def returning_id_sql():
    """Return SQL clause to get last inserted id, or empty for SQLite."""
    if get_db_type() == "postgresql":
        return "RETURNING id"
    return ""


def get_table_columns(cursor, table_name):
    """Get list of column names for a table, cross-db compatible."""
    if get_db_type() == "postgresql":
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
            (table_name,),
        )
    else:
        cursor.execute(f"PRAGMA table_info({table_name})")
    rows = cursor.fetchall()

    if get_db_type() == "postgresql":
        return {row["column_name"] if isinstance(row, dict) else row[0] for row in rows}
    return {row[1] for row in rows}


class UniversalRow:
    """A row that supports both dict-style and index-style access.

    Wraps either a dict (PostgreSQL) or sqlite3.Row / tuple (SQLite).
    This allows existing code using both row["col"] and row[0] to work.
    """

    def __init__(self, data, keys):
        self._data = data
        self._keys = keys

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._data[self._keys[key]]
        return self._data[key]

    def __contains__(self, key):
        return key in self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __iter__(self):
        return iter(self._data.values())

    def __len__(self):
        return len(self._keys)

    def __repr__(self):
        return repr(self._data)

    def __bool__(self):
        return bool(self._data)

    def __eq__(self, other):
        if isinstance(other, UniversalRow):
            return self._data == other._data
        return self._data == other

    def __hash__(self):
        return id(self)


def _make_universal(row, cursor_desc):
    """Convert a raw row to UniversalRow if needed."""
    if row is None:
        return None
    if isinstance(row, dict):
        keys = [d[0] for d in cursor_desc] if cursor_desc else list(row.keys())
        return UniversalRow(row, keys)
    if hasattr(row, "keys") and callable(row.keys):
        try:
            keys = list(row.keys())
            return UniversalRow(dict(row), keys)
        except Exception:
            pass
    if isinstance(row, (list, tuple)):
        keys = [d[0] for d in cursor_desc] if cursor_desc else list(range(len(row)))
        return UniversalRow(dict(zip(keys, row)), keys)
    return row


def adapt_sql(sql):
    """Convert SQLite-specific SQL to the current DB's dialect.

    Handles:
    - ? placeholders → %s (PostgreSQL)
    - AUTOINCREMENT → (removed, SERIAL/BIGSERIAL is implicit in PG)
    - INTEGER PRIMARY KEY AUTOINCREMENT → BIGSERIAL PRIMARY KEY
    """
    if get_db_type() == "postgresql":
        sql = sql.replace("?", "%s")
        sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "BIGSERIAL PRIMARY KEY")
        sql = sql.replace("INTEGER AUTOINCREMENT", "BIGSERIAL")
        if sql.startswith("INSERT OR IGNORE INTO "):
            sql = sql.replace("INSERT OR IGNORE INTO ", "INSERT INTO ", 1)
            sql += " ON CONFLICT DO NOTHING"
    return sql


class CompatCursor:
    """Cursor wrapper that transparently adapts ? placeholders for PostgreSQL.

    Also provides .lastval as a cross-db way to get the last inserted id.
    """

    def __init__(self, cursor, connection=None):
        self._cursor = cursor
        self._connection = connection
        self.lastrowid = None

    def execute(self, sql, params=None):
        sql = adapt_sql(sql)
        result = self._cursor.execute(sql, params) if params else self._cursor.execute(sql)
        try:
            self.lastrowid = self._cursor.lastrowid
        except Exception:
            pass
        return result

    def executemany(self, sql, params_list):
        sql = adapt_sql(sql)
        return self._cursor.executemany(sql, params_list)

    def fetchone(self):
        row = self._cursor.fetchone()
        return _make_universal(row, self._cursor.description)

    def fetchall(self):
        rows = self._cursor.fetchall()
        desc = self._cursor.description
        return [_make_universal(r, desc) for r in rows]

    def fetchmany(self, size=None):
        if size is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(size)

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    def close(self):
        self._cursor.close()

    def __iter__(self):
        return iter(self._cursor)

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class CompatConnection:
    """Connection wrapper that returns CompatCursor instances."""

    def __init__(self, connection):
        self._conn = connection

    def cursor(self):
        raw = self._conn.cursor()
        return CompatCursor(raw, self)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    @property
    def raw(self):
        return self._conn

    def __getattr__(self, name):
        return getattr(self._conn, name)
