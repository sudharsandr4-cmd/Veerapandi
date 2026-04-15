import sqlite3
import os
from datetime import datetime

# Use absolute path for database to ensure it works in Railway
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(DB_DIR, 'voters.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create Booths table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS booths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booth_number TEXT UNIQUE NOT NULL,
            booth_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Voters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT UNIQUE NOT NULL,
            voter_name TEXT NOT NULL,
            house_number TEXT,
            booth_id INTEGER NOT NULL,
            booth_number TEXT NOT NULL,
            phone_number TEXT,
            status TEXT DEFAULT 'not_visited',
            custom_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booth_id) REFERENCES booths(id)
        )
    ''')
    
    # Create index for faster searches
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_voter_name ON voters(voter_name)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_voter_id ON voters(voter_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_phone_number ON voters(phone_number)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_booth_id ON voters(booth_id)
    ''')
    
    conn.commit()
    conn.close()

def add_booth(booth_number, booth_name):
    """Add a new booth to the database"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO booths (booth_number, booth_name) VALUES (?, ?)',
            (booth_number, booth_name)
        )
        conn.commit()
        booth_id = cursor.lastrowid
        conn.close()
        return booth_id
    except sqlite3.IntegrityError:
        conn.close()
        # Booth already exists, fetch its ID
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM booths WHERE booth_number = ?', (booth_number,))
        result = cursor.fetchone()
        conn.close()
        return result['id'] if result else None

def add_voter(voter_id, voter_name, booth_number, house_number=None):
    """Add a new voter to the database"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get booth ID
    cursor.execute('SELECT id FROM booths WHERE booth_number = ?', (booth_number,))
    booth_result = cursor.fetchone()
    
    if booth_result is None:
        conn.close()
        return None
    
    booth_id = booth_result['id']
    
    try:
        cursor.execute(
            '''INSERT INTO voters (voter_id, voter_name, booth_id, booth_number, house_number) 
               VALUES (?, ?, ?, ?, ?)''',
            (voter_id, voter_name, booth_id, booth_number, house_number)
        )
        conn.commit()
        voter_id_db = cursor.lastrowid
        conn.close()
        return voter_id_db
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_all_booths():
    """Get all booths"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, booth_number, booth_name FROM booths ORDER BY booth_number')
    booths = cursor.fetchall()
    conn.close()
    return [dict(booth) for booth in booths]

def get_voters_by_booth(booth_id):
    """Get all voters in a booth"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT id, voter_id, voter_name, house_number, booth_number, phone_number, status, custom_notes 
           FROM voters WHERE booth_id = ? ORDER BY voter_name''',
        (booth_id,)
    )
    voters = cursor.fetchall()
    conn.close()
    return [dict(voter) for voter in voters]

def search_voters(search_term, booth_id=None):
    """Search voters by name or voter ID"""
    conn = get_db()
    cursor = conn.cursor()
    search_param = f'%{search_term}%'
    
    if booth_id:
        cursor.execute(
            '''SELECT id, voter_id, voter_name, house_number, booth_number, phone_number, status, custom_notes 
               FROM voters 
               WHERE booth_id = ? AND (voter_name LIKE ? OR voter_id LIKE ? OR phone_number LIKE ?)
               ORDER BY voter_name''',
            (booth_id, search_param, search_param, search_param)
        )
    else:
        cursor.execute(
            '''SELECT id, voter_id, voter_name, house_number, booth_number, phone_number, status, custom_notes 
               FROM voters 
               WHERE voter_name LIKE ? OR voter_id LIKE ? OR phone_number LIKE ?
               ORDER BY voter_name''',
            (search_param, search_param, search_param)
        )
    
    voters = cursor.fetchall()
    conn.close()
    return [dict(voter) for voter in voters]
