import sqlite3

conn = sqlite3.connect('users.db')  # Creates the database file
cursor = conn.cursor()

# Create the users table
cursor.execute('''
    CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    chips INTEGER DEFAULT 0
);
''')

conn.commit()
conn.close()

print("Database initialized successfully.")
