
import sqlite3

conn = sqlite3.connect("mocktest.db")

cursor = conn.cursor()

# Users

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    mobile TEXT UNIQUE,
    password TEXT NOT NULL
)
""")

# Admin

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# Categories

cursor.execute("""
CREATE TABLE IF NOT EXISTS categories(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL
)
""")

# Tests

cursor.execute("""
CREATE TABLE IF NOT EXISTS tests(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL,
    category_id INTEGER,
    duration INTEGER
)
""")

# Questions

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER,
    question TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    answer TEXT
)
""")

# Results

cursor.execute("""
CREATE TABLE IF NOT EXISTS results(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    test_id INTEGER,
    score INTEGER
)
""")

# Default Admin

cursor.execute("""
INSERT OR IGNORE INTO admin(id, username, password)
VALUES(1,'admin','admin123')
""")

conn.commit()
conn.close()

print("Mock Test Database Created Successfully")
