import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

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

    # Create Users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
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

    # Add serial_number column if it doesn't already exist from a previous schema
    try:
        cursor.execute('ALTER TABLE voters ADD COLUMN serial_number TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Check if any users exist. If not, create a default user.
    cursor.execute('SELECT COUNT(id) FROM users')
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        print("\n--- NO USERS FOUND IN DATABASE ---")
        print("Creating a default user to ensure the application is accessible on first run.")
        default_username = 'adminveera1'
        default_password = 'veerapandi911'
        try:
            cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (default_username, generate_password_hash(default_password))
            )
            conn.commit()
            print("--> Default user created successfully!")
            print(f"--> Username: {default_username}")
            print(f"--> Password: {default_password}")
            print("--> You can now log in with these credentials.\n")
        except sqlite3.IntegrityError:
            print("Default user appears to already exist.")

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

def add_user(username, password):
    """Adds a new user with a hashed password."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"User {username} already exists.")
    finally:
        conn.close()

def get_user_by_username(username):
    """Retrieves a user by their username."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_users():
    """Retrieves all users from the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users ORDER BY username')
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]


def upsert_voters(voters_data: list):
    """
    Upserts a list of voters from a pandas DataFrame.
    If voter_id exists, it updates the record. Otherwise, it inserts a new one.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    added_count = 0
    updated_count = 0
    
    # Ensure all booths from the file exist before processing voters
    booth_numbers = {v['booth_number'] for v in voters_data if v.get('booth_number')}
    for booth_num in booth_numbers:
        cursor.execute('SELECT id FROM booths WHERE booth_number = ?', (booth_num,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO booths (booth_number, booth_name) VALUES (?, ?)', (booth_num, f'Booth {booth_num}'))

    for voter in voters_data:
        cursor.execute('SELECT id FROM voters WHERE voter_id = ?', (voter['voter_id'],))
        existing_voter = cursor.fetchone()
        
        cursor.execute('SELECT id FROM booths WHERE booth_number = ?', (voter['booth_number'],))
        booth_row = cursor.fetchone()
        booth_id = booth_row['id'] if booth_row else None

        serial = voter.get('serial_number')

        if existing_voter:
            cursor.execute(
                'UPDATE voters SET voter_name = ?, house_number = ?, booth_id = ?, booth_number = ?, serial_number = ? WHERE id = ?',
                (voter['voter_name'], voter.get('house_number'), booth_id, voter['booth_number'], serial, existing_voter['id'])
            )
            updated_count += 1
        else:
            cursor.execute(
                '''INSERT INTO voters (voter_id, voter_name, booth_id, booth_number, house_number, serial_number) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (voter['voter_id'], voter['voter_name'], booth_id, voter['booth_number'], voter.get('house_number'), serial)
            )
            added_count += 1
            
    conn.commit()
    conn.close()
    return added_count, updated_count

def add_voter(voter_id, voter_name, booth_number, house_number=None, serial_number=None):
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
            '''INSERT INTO voters (voter_id, voter_name, booth_id, booth_number, house_number, serial_number) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (voter_id, voter_name, booth_id, booth_number, house_number, serial_number)
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
        '''SELECT id, voter_id, voter_name, house_number, booth_number, phone_number, status, custom_notes, serial_number 
           FROM voters WHERE booth_id = ? ORDER BY CAST(serial_number AS INTEGER), voter_name''',
        (booth_id,)
    )
    voters = cursor.fetchall()
    conn.close()
    return [dict(voter) for voter in voters]

def search_voters(search_term, booth_id=None):
    """Search voters by serial number, name or voter ID"""
    conn = get_db()
    cursor = conn.cursor()
    search_param = f'%{search_term}%'
    
    if booth_id:
        cursor.execute(
            '''SELECT id, voter_id, voter_name, house_number, booth_number, phone_number, status, custom_notes, serial_number 
               FROM voters 
               WHERE booth_id = ? AND (serial_number = ? OR voter_name LIKE ? OR voter_id LIKE ? OR phone_number LIKE ?)
               ORDER BY CAST(serial_number AS INTEGER), voter_name''',
            (booth_id, search_term, search_param, search_param, search_param)
        )
    else:
        cursor.execute(
            '''SELECT id, voter_id, voter_name, house_number, booth_number, phone_number, status, custom_notes, serial_number 
               FROM voters 
               WHERE serial_number = ? OR voter_name LIKE ? OR voter_id LIKE ? OR phone_number LIKE ?
               ORDER BY CAST(serial_number AS INTEGER), voter_name''',
            (search_term, search_param, search_param, search_param)
        )
    
    voters = cursor.fetchall()
    conn.close()
    return [dict(voter) for voter in voters]

def update_voter(voter_id, status=None, phone_number=None, custom_notes=None, house_number=None):
    """Update voter information"""
    conn = get_db()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if status is not None:
        updates.append("status = ?" )
        params.append(status)
    if phone_number is not None:
        updates.append("phone_number = ?" )
        params.append(phone_number)
    if custom_notes is not None:
        updates.append("custom_notes = ?" )
        params.append(custom_notes)
    if house_number is not None:
        updates.append("house_number = ?")
        params.append(house_number)
    
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP" )
        params.append(voter_id)
        set_clause = ', '.join(updates)
        query = f'''UPDATE voters SET {set_clause} WHERE id = ?'''
        cursor.execute(query, params)
    
    conn.commit()
    conn.close()

def get_voter_stats(booth_id=None):
    """Get statistics about voters"""
    # "Visited" is now defined as having a phone number added.
    conn = get_db()
    cursor = conn.cursor()
    
    if booth_id:
        cursor.execute(
            '''SELECT COUNT(*) as total, 
                      SUM(CASE WHEN phone_number IS NOT NULL AND phone_number != '' THEN 1 ELSE 0 END) as visited
               FROM voters WHERE booth_id = ?''',
            (booth_id,)
        )
    else:
        cursor.execute(
            '''SELECT COUNT(*) as total, 
                      SUM(CASE WHEN phone_number IS NOT NULL AND phone_number != '' THEN 1 ELSE 0 END) as visited
               FROM voters'''
        )
    
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else {'total': 0, 'visited': 0}

def clear_all_data():
    """Clear all data from database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM voters')
    cursor.execute('DELETE FROM booths')
    conn.commit()
    conn.close()
