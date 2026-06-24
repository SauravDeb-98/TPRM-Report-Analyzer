import sqlite3
import os

DB_PATH = 'feedback.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT,
            filename TEXT,
            is_positive BOOLEAN,
            comments TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_feedback(vendor_name, filename, is_positive, comments=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (vendor_name, filename, is_positive, comments)
        VALUES (?, ?, ?, ?)
    ''', (vendor_name, filename, is_positive, comments))
    conn.commit()
    conn.close()
