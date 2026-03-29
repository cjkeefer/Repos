#!/usr/bin/env python3
"""Test script for SQLite CRUD UI functionality."""

import sqlite3
import pandas as pd
import sys
import os

def test_database_operations():
    """Test basic database operations."""
    print("Testing SQLite CRUD UI functionality...")

    # Test database connection
    try:
        conn = sqlite3.connect('sample_crud.db')
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

    # Test table listing
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        print(f"✓ Found tables: {', '.join(table_names)}")

        if 'users' not in table_names or 'products' not in table_names:
            print("✗ Expected tables not found")
            return False

    except Exception as e:
        print(f"✗ Table listing failed: {e}")
        return False

    # Test data loading
    try:
        for table in ['users', 'products']:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            print(f"✓ Loaded {len(df)} rows from {table} table")
            print(f"  Columns: {', '.join(df.columns)}")
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
        return False

    # Test CRUD operations
    try:
        # CREATE
        cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                      ('Test User', 'test@example.com', 99))
        new_id = cursor.lastrowid
        conn.commit()
        print(f"✓ Created new user with ID: {new_id}")

        # READ
        cursor.execute("SELECT * FROM users WHERE id = ?", (new_id,))
        user = cursor.fetchone()
        print(f"✓ Read user: {user}")

        # UPDATE
        cursor.execute("UPDATE users SET age = ? WHERE id = ?", (100, new_id))
        conn.commit()
        print("✓ Updated user age to 100")

        # DELETE
        cursor.execute("DELETE FROM users WHERE id = ?", (new_id,))
        conn.commit()
        print("✓ Deleted test user")

    except Exception as e:
        print(f"✗ CRUD operations failed: {e}")
        return False

    conn.close()
    print("✓ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_database_operations()
    sys.exit(0 if success else 1)