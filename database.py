import sqlite3
import os
from pathlib import Path

def init_db(db_path="data/edututor.db"):
    """Initialize the SQLite database with proper error handling"""
    db_file = Path(db_path)
    
    # Ensure directory exists
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Create users table if not exists
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('student', 'educator')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create quiz_results table if not exists
        c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        conn.commit()
        return conn
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        # If database is corrupted, delete and recreate
        if db_file.exists():
            db_file.unlink()
        return init_db(db_path)  # Retry
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise