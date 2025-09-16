import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
from config import DATABASE_PATH, DATETIME_FORMAT, get_today_log_file

class AttendanceDatabase:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                email TEXT,
                department TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date TEXT NOT NULL,
                confidence REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, name, email=None, department=None):
        """Add a new user to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (name, email, department)
                VALUES (?, ?, ?)
            ''', (name, email, department))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # User already exists
    
    def get_user_by_name(self, name):
        """Get user information by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
        user = cursor.fetchone()
        conn.close()
        
        return user
    
    def get_all_users(self):
        """Get all users from database"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM users ORDER BY name', conn)
        conn.close()
        return df
    
    def mark_attendance(self, name, confidence=None):
        """Mark attendance for a user"""
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        
        # Check if user already marked attendance today within cooldown period
        if self.is_recent_attendance(name, minutes=5):
            return False, "Attendance already marked recently"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user ID
        user = self.get_user_by_name(name)
        user_id = user[0] if user else None
        
        # Insert attendance record
        cursor.execute('''
            INSERT INTO attendance (user_id, name, timestamp, date, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, now.strftime(DATETIME_FORMAT), date_str, confidence))
        
        conn.commit()
        conn.close()
        
        # Also log to CSV file
        self.log_to_csv(name, now, confidence)
        
        return True, "Attendance marked successfully"
    
    def is_recent_attendance(self, name, minutes=5):
        """Check if user has recent attendance within specified minutes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        cursor.execute('''
            SELECT COUNT(*) FROM attendance 
            WHERE name = ? AND timestamp > ?
        ''', (name, cutoff_time.strftime(DATETIME_FORMAT)))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def log_to_csv(self, name, timestamp, confidence):
        """Log attendance to CSV file"""
        log_file = get_today_log_file()
        
        # Create CSV with headers if it doesn't exist
        if not os.path.exists(log_file):
            df = pd.DataFrame(columns=['Name', 'Timestamp', 'Date', 'Time', 'Confidence'])
            df.to_csv(log_file, index=False)
        
        # Append new record
        new_record = {
            'Name': name,
            'Timestamp': timestamp.strftime(DATETIME_FORMAT),
            'Date': timestamp.strftime('%Y-%m-%d'),
            'Time': timestamp.strftime('%H:%M:%S'),
            'Confidence': confidence if confidence else 'N/A'
        }
        
        df = pd.DataFrame([new_record])
        df.to_csv(log_file, mode='a', header=False, index=False)
    
    def get_attendance_by_date(self, date_str):
        """Get attendance records for a specific date"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT a.name, a.timestamp, a.confidence, u.email, u.department
            FROM attendance a
            LEFT JOIN users u ON a.user_id = u.id
            WHERE a.date = ?
            ORDER BY a.timestamp
        ''', conn, params=(date_str,))
        conn.close()
        return df
    
    def get_attendance_summary(self, start_date=None, end_date=None):
        """Get attendance summary for date range"""
        conn = sqlite3.connect(self.db_path)
        
        if start_date and end_date:
            df = pd.read_sql_query('''
                SELECT date, COUNT(*) as total_attendance
                FROM attendance
                WHERE date BETWEEN ? AND ?
                GROUP BY date
                ORDER BY date DESC
            ''', conn, params=(start_date, end_date))
        else:
            df = pd.read_sql_query('''
                SELECT date, COUNT(*) as total_attendance
                FROM attendance
                GROUP BY date
                ORDER BY date DESC
                LIMIT 30
            ''', conn)
        
        conn.close()
        return df
    
    def delete_user(self, name):
        """Delete a user and their attendance records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete attendance records first
        cursor.execute('DELETE FROM attendance WHERE name = ?', (name,))
        
        # Delete user
        cursor.execute('DELETE FROM users WHERE name = ?', (name,))
        
        conn.commit()
        deleted_rows = cursor.rowcount
        conn.close()
        
        return deleted_rows > 0

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19

# Updated: 2025-12-19
