import sqlite3

conn = sqlite3.connect('weather.db', check_same_thread=False) #check_same_thread=False
cur = conn.cursor()
# Підключення до бази даних
def createTable():
    # Створення таблиці, якщо вона не існує
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            temperature REAL NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            minT TEXT NOT NULL,
            maxT TEXT NOT NULL,
            feel TEXT NOT NULL,
            pres TEXT NOT NULL,
            hum TEXT NOT NULL,
            wind TEXT NOT NULL,
            icon TEXT NOT NULL,
            day TEXT NOT NULL
        )
    """)
    conn.commit()