import sqlite3

conn = sqlite3.connect("news.db")
c = conn.cursor()

def execute(query, *args):
    result = c.execute(query, args)
    conn.commit()
    return result
