import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# Teachers table
c.execute("""
CREATE TABLE IF NOT EXISTS teachers(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

# Students table
c.execute("""
CREATE TABLE IF NOT EXISTS students(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
roll TEXT,
phone TEXT
)
""")

# Attendance table
c.execute("""
CREATE TABLE IF NOT EXISTS attendance(
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER,
status TEXT,
date TEXT
)
""")

# Insert admin only if not exists
c.execute("SELECT * FROM teachers WHERE username='admin'")
admin = c.fetchone()

if not admin:
    c.execute("INSERT INTO teachers(username,password) VALUES('admin','admin123')")

conn.commit()
conn.close()

print("Database created successfully")
