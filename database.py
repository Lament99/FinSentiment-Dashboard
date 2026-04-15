import sqlite3

DB_NAME = "finsentiment.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            title TEXT,
            description TEXT,
            published_at TEXT,
            source TEXT,
            url TEXT UNIQUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            label TEXT,
            score REAL,
            FOREIGN KEY (article_id) REFERENCES articles(id)
        )
    """)
    conn.commit()
    conn.close()

def insert_article(ticker, title, description, published_at, source, url):
    conn = get_connection()
    try:
        cursor = conn.execute("""
            INSERT INTO articles (ticker, title, description, published_at, source, url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ticker, title, description, published_at, source, url))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # duplicate URL, skip
    finally:
        conn.close()

def insert_sentiment(article_id, label, score):
    conn = get_connection()
    conn.execute("""
        INSERT INTO sentiment (article_id, label, score)
        VALUES (?, ?, ?)
    """, (article_id, label, score))
    conn.commit()
    conn.close()

def get_articles_by_ticker(ticker):
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.id, a.title, a.published_at, s.label, s.score
        FROM articles a
        LEFT JOIN sentiment s ON a.id = s.article_id
        WHERE a.ticker = ?
        ORDER BY a.published_at DESC
    """, (ticker,)).fetchall()
    conn.close()
    return rows