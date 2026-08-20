import sqlite3
from datetime import datetime

DB_NAME = 'study_planner.db'

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            deadline TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(name, email, password):
    """Add a new user"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (name, email, password)
        VALUES (?, ?, ?)
    ''', (name, email, password))
    
    conn.commit()
    conn.close()

def get_user(email):
    """Get user by email"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return tuple(user)
    return None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return tuple(user)
    return None

def add_task(user_id, title, description, deadline, status='pending'):
    """Add a new task"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO tasks (user_id, title, description, deadline, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, title, description, deadline, status))
    
    conn.commit()
    conn.close()

def get_user_tasks(user_id):
    """Get all tasks for a user"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM tasks WHERE user_id = ?
        ORDER BY deadline ASC
    ''', (user_id,))
    
    tasks = cursor.fetchall()
    conn.close()
    
    return [tuple(task) for task in tasks]

def get_task_by_id(task_id, user_id):
    """Get specific task by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM tasks WHERE id = ? AND user_id = ?
    ''', (task_id, user_id))
    
    task = cursor.fetchone()
    conn.close()
    
    if task:
        return tuple(task)
    return None

def update_task(task_id, status):
    """Update task status"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE tasks SET status = ? WHERE id = ?
    ''', (status, task_id))
    
    conn.commit()
    conn.close()

def delete_task(task_id):
    """Delete a task"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    
    conn.commit()
    conn.close()
