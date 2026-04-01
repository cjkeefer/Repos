import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'chores.db')

def get_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with chores, menu, and grocery tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create chores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            assigned_to TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            due_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create menu table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients TEXT,
            day TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create grocery table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grocery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity TEXT,
            purchased BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if chores table has data, if not add sample chores
    cursor.execute('SELECT COUNT(*) FROM chores')
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_chores = [
            ('Wash dishes', 'John', False, '2026-03-31'),
            ('Mow the lawn', 'Dad', False, '2026-04-01'),
            ('Vacuum living room', 'Sarah', True, '2026-03-30'),
            ('Laundry', 'Mom', False, '2026-03-31'),
        ]
        
        for title, assigned_to, completed, due_date in sample_chores:
            cursor.execute(
                '''INSERT INTO chores (title, assigned_to, completed, due_date)
                   VALUES (?, ?, ?, ?)''',
                (title, assigned_to, completed, due_date)
            )
    
    # Sample menu data
    cursor.execute('SELECT COUNT(*) FROM menu')
    menu_count = cursor.fetchone()[0]
    
    if menu_count == 0:
        sample_menu = [
            ('Spaghetti', 'Pasta, Tomato Sauce, Meatballs', 'Monday'),
            ('Chicken Tacos', 'Chicken, Tortillas, Lettuce, Cheese', 'Tuesday'),
            ('Grilled Salmon', 'Salmon, Broccoli, Rice', 'Wednesday'),
        ]
        
        for name, ingredients, day in sample_menu:
            cursor.execute(
                '''INSERT INTO menu (name, ingredients, day)
                   VALUES (?, ?, ?)''',
                (name, ingredients, day)
            )
    
    conn.commit()
    conn.close()


def get_all_chores():
    """Get all chores from the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, assigned_to, completed, due_date FROM chores ORDER BY created_at DESC')
        rows = cursor.fetchall()
        chores = []
        for row in rows:
            chores.append({
                'id': row[0],
                'title': row[1],
                'assigned_to': row[2],
                'completed': bool(row[3]),
                'due_date': row[4]
            })
        conn.close()
        return chores
    except Exception as e:
        print(f"Error in get_all_chores: {str(e)}")
        raise

def add_chore(title, assigned_to, due_date):
    """Add a new chore to the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO chores (title, assigned_to, due_date, completed)
               VALUES (?, ?, ?, 0)''',
            (title, assigned_to, due_date)
        )
        conn.commit()
        chore_id = cursor.lastrowid
        
        # Return the created chore
        cursor.execute('SELECT id, title, assigned_to, completed, due_date FROM chores WHERE id = ?', (chore_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'assigned_to': row[2],
                'completed': bool(row[3]),
                'due_date': row[4]
            }
        return None
    except Exception as e:
        print(f"Error in add_chore: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise

def toggle_chore(chore_id):
    """Toggle the completed status of a chore"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get current status
        cursor.execute('SELECT id, completed FROM chores WHERE id = ?', (chore_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        current_status = int(result[1])
        new_status = 1 - current_status
        
        # Update the status
        cursor.execute(
            '''UPDATE chores SET completed = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (new_status, chore_id)
        )
        conn.commit()
        
        # Return the updated chore
        cursor.execute('SELECT id, title, assigned_to, completed, due_date FROM chores WHERE id = ?', (chore_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'assigned_to': row[2],
                'completed': bool(row[3]),
                'due_date': row[4]
            }
        return None
    except Exception as e:
        print(f"Error in toggle_chore: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise

def delete_chore(chore_id):
    """Delete a chore from the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM chores WHERE id = ?', (chore_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
    except Exception as e:
        print(f"Error in delete_chore: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise

def update_chore(chore_id, title=None, assigned_to=None, due_date=None):
    """Update a chore in the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Build the update query dynamically
        updates = []
        params = []
        
        if title is not None:
            updates.append('title = ?')
            params.append(title)
        if assigned_to is not None:
            updates.append('assigned_to = ?')
            params.append(assigned_to)
        if due_date is not None:
            updates.append('due_date = ?')
            params.append(due_date)
        
        if not updates:
            conn.close()
            return None
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(chore_id)
        
        query = f"UPDATE chores SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        
        # Return the updated chore
        cursor.execute('SELECT id, title, assigned_to, completed, due_date FROM chores WHERE id = ?', (chore_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'title': row[1],
                'assigned_to': row[2],
                'completed': bool(row[3]),
                'due_date': row[4]
            }
        return None
    except Exception as e:
        print(f"Error in update_chore: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise

# Menu CRUD functions
def get_all_menu():
    """Get all menu items"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, ingredients, day FROM menu ORDER BY created_at DESC')
        rows = cursor.fetchall()
        items = []
        for row in rows:
            items.append({
                'id': row[0],
                'name': row[1],
                'ingredients': row[2],
                'day': row[3]
            })
        conn.close()
        return items
    except Exception as e:
        print(f"Error in get_all_menu: {str(e)}")
        raise

def add_menu_item(name, day, ingredients=None):
    """Add a new menu item"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO menu (name, ingredients, day)
               VALUES (?, ?, ?)''',
            (name, ingredients, day)
        )
        conn.commit()
        item_id = cursor.lastrowid
        
        cursor.execute('SELECT id, name, ingredients, day FROM menu WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'ingredients': row[2],
                'day': row[3]
            }
        return None
    except Exception as e:
        print(f"Error in add_menu_item: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise

def delete_menu_item(item_id):
    """Delete a menu item"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM menu WHERE id = ?', (item_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
    except Exception as e:
        print(f"Error in delete_menu_item: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise

# Grocery CRUD functions
def get_all_grocery():
    """Get all grocery items"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, quantity, purchased FROM grocery ORDER BY purchased ASC, created_at DESC')
        rows = cursor.fetchall()
        items = []
        for row in rows:
            items.append({
                'id': row[0],
                'name': row[1],
                'quantity': row[2],
                'purchased': bool(row[3])
            })
        conn.close()
        return items
    except Exception as e:
        print(f"Error in get_all_grocery: {str(e)}")
        raise

def add_grocery_item(name, quantity=None):
    """Add a new grocery item"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO grocery (name, quantity, purchased)
               VALUES (?, ?, 0)''',
            (name, quantity)
        )
        conn.commit()
        item_id = cursor.lastrowid
        
        cursor.execute('SELECT id, name, quantity, purchased FROM grocery WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'quantity': row[2],
                'purchased': bool(row[3])
            }
        return None
    except Exception as e:
        print(f"Error in add_grocery_item: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise

def toggle_grocery_purchased(item_id):
    """Toggle purchased status of a grocery item"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, purchased FROM grocery WHERE id = ?', (item_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        current_status = int(result[1])
        new_status = 1 - current_status
        
        cursor.execute(
            '''UPDATE grocery SET purchased = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (new_status, item_id)
        )
        conn.commit()
        
        cursor.execute('SELECT id, name, quantity, purchased FROM grocery WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'quantity': row[2],
                'purchased': bool(row[3])
            }
        return None
    except Exception as e:
        print(f"Error in toggle_grocery_purchased: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise

def delete_grocery_item(item_id):
    """Delete a grocery item"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM grocery WHERE id = ?', (item_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
    except Exception as e:
        print(f"Error in delete_grocery_item: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise
