#!/usr/bin/env python3
"""
SQLite CRUD UI Launcher

This script provides a convenient way to launch the SQLite CRUD UI application.
"""

import sys
import os

def main():
    """Launch the SQLite CRUD UI application."""
    try:
        # Import and run the main application
        from main import main as app_main
        app_main()
    except ImportError as e:
        print(f"Error importing application: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()