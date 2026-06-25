import sqlite3

DB_NAME = "app.db"


def conn():
    c = sqlite3.connect(DB_NAME)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    c = conn()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT,
        plan TEXT DEFAULT 'free',
        used INTEGER DEFAULT 0,
        sub_end INTEGER DEFAULT 0,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        tool TEXT,
        product TEXT,
        result TEXT,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """)

    c.commit()
    c.close()


def create_user(email, password_hash, code=""):
    c = conn()

    c.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, password_hash)
    )

    c.commit()
    c.close()


def get_user_by_email(email):
    c = conn()

    u = c.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    ).fetchone()

    c.close()
    return u


def get_user_by_id(uid):
    c = conn()

    u = c.execute(
        "SELECT * FROM users WHERE id=?",
        (uid,)
    ).fetchone()

    c.close()
    return u


def update_usage(uid, used):
    c = conn()

    c.execute(
        "UPDATE users SET used=? WHERE id=?",
        (used, uid)
    )

    c.commit()
    c.close()


def activate_pro(uid, sub_end):
    c = conn()

    c.execute(
        "UPDATE users SET plan='pro', sub_end=? WHERE id=?",
        (sub_end, uid)
    )

    c.commit()
    c.close()


def save_generation(uid, tool, product, result):
    c = conn()

    c.execute(
        "INSERT INTO events (user_id, tool, product, result) VALUES (?, ?, ?, ?)",
        (uid, tool, product, result)
    )

    c.commit()
    c.close()


def get_generations(uid):
    c = conn()

    rows = c.execute(
        "SELECT * FROM events WHERE user_id=? ORDER BY id DESC",
        (uid,)
    ).fetchall()

    c.close()
    return rows


def get_stats():
    c = conn()

    users = c.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    pro = c.execute(
        "SELECT COUNT(*) FROM users WHERE plan='pro'"
    ).fetchone()[0]

    c.close()

    return {
        "users": users,
        "pro": pro
    }