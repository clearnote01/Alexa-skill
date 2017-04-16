import sqlite3

conn = sqlite3.connect("news.db")
c = conn.cursor()

def create_tables():
    c.execute("""
        CREATE TABLE
        IF NOT EXISTS news(
            id SERIAL,
            news TEXT,
            location TEXT
        )
    """)
    c.execute("""
        CREATE TABLE
        IF NOT EXISTS opinions(
            news_id INT,
            user_id TEXT,
            vote_positive INT,
            vote_negative INT,
            opinion TEXT
        )
    """)
    c.execute("""
        CREATE TABLE
        iF NOT EXISTS user(
            user_id TEXT,
            newsCount INT,
            location TEXT
        )
    """)

if __name__ == '__main__':
    create_tables()
