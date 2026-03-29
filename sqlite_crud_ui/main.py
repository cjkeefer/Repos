"""SQLite CRUD UI - A graphical interface for managing SQLite databases."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
import threading


class SQLiteCRUDApp:
    """Main application class for SQLite CRUD operations."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SQLite CRUD Manager")
        self.root.geometry("1200x800")

        # Database connection
        self.conn: Optional[sqlite3.Connection] = None
        self.db_path: Optional[str] = None

        # Current table data
        self.current_table: Optional[str] = None
        self.table_data: Optional[pd.DataFrame] = None

        self.setup_ui()
        self.center_window()

    def setup_ui(self):
        """Set up the main UI components."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Database connection section
        db_frame = ttk.LabelFrame(main_frame, text="Database Connection", padding="5")
        db_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(db_frame, text="Database:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.db_entry = ttk.Entry(db_frame, width=50)
        self.db_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(db_frame, text="Browse", command=self.browse_database).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(db_frame, text="Connect", command=self.connect_database).grid(row=0, column=3)
        ttk.Button(db_frame, text="Disconnect", command=self.disconnect_database).grid(row=0, column=4, padx=(5, 0))

        db_frame.columnconfigure(1, weight=1)

        # Tables section
        tables_frame = ttk.LabelFrame(main_frame, text="Tables", padding="5")
        tables_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Tables listbox with scrollbar
        tables_scrollbar = ttk.Scrollbar(tables_frame)
        tables_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.tables_listbox = tk.Listbox(tables_frame, height=10, yscrollcommand=tables_scrollbar.set)
        self.tables_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tables_listbox.bind('<<ListboxSelect>>', self.on_table_select)

        tables_scrollbar.config(command=self.tables_listbox.yview)
        tables_frame.columnconfigure(0, weight=1)
        tables_frame.rowconfigure(0, weight=1)

        # CRUD operations section
        crud_frame = ttk.LabelFrame(main_frame, text="CRUD Operations", padding="5")
        crud_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # CRUD buttons
        button_frame = ttk.Frame(crud_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

        ttk.Button(button_frame, text="Create", command=self.create_record).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Update", command=self.update_record).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="Delete", command=self.delete_record).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(button_frame, text="Refresh", command=self.refresh_table).grid(row=0, column=3)

        # Data table section
        table_frame = ttk.LabelFrame(main_frame, text="Table Data", padding="5")
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Treeview for displaying table data
        self.tree = ttk.Treeview(table_frame)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbars for treeview
        tree_scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=tree_scrollbar_y.set)

        tree_scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        tree_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=tree_scrollbar_x.set)

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def browse_database(self):
        """Browse for a SQLite database file."""
        filename = filedialog.askopenfilename(
            title="Select SQLite Database",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.db_entry.delete(0, tk.END)
            self.db_entry.insert(0, filename)

    def connect_database(self):
        """Connect to the SQLite database."""
        db_path = self.db_entry.get().strip()
        if not db_path:
            messagebox.showerror("Error", "Please select a database file.")
            return

        try:
            self.conn = sqlite3.connect(db_path)
            self.db_path = db_path
            self.status_var.set(f"Connected to: {db_path}")
            self.load_tables()
            messagebox.showinfo("Success", f"Connected to database: {db_path}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database:\n{str(e)}")

    def disconnect_database(self):
        """Disconnect from the current database."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.db_path = None
            self.current_table = None
            self.table_data = None
            self.tables_listbox.delete(0, tk.END)
            self.clear_treeview()
            self.status_var.set("Disconnected")
            messagebox.showinfo("Disconnected", "Database connection closed.")

    def load_tables(self):
        """Load table names from the database."""
        if not self.conn:
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = cursor.fetchall()

            self.tables_listbox.delete(0, tk.END)
            for table in tables:
                self.tables_listbox.insert(tk.END, table[0])

            self.status_var.set(f"Loaded {len(tables)} tables")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tables:\n{str(e)}")

    def on_table_select(self, event):
        """Handle table selection from the listbox."""
        selection = self.tables_listbox.curselection()
        if selection:
            table_name = self.tables_listbox.get(selection[0])
            self.load_table_data(table_name)

    def load_table_data(self, table_name: str):
        """Load data from the selected table."""
        if not self.conn:
            return

        try:
            # Get column information
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            # Load table data
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
            self.table_data = df
            self.current_table = table_name

            # Update treeview
            self.update_treeview(column_names, df)

            self.status_var.set(f"Loaded table: {table_name} ({len(df)} rows)")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table data:\n{str(e)}")

    def update_treeview(self, columns: List[str], df: pd.DataFrame):
        """Update the treeview with table data."""
        # Clear existing data
        self.clear_treeview()

        # Configure columns
        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        # Add column headings
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=100, minwidth=50)

        # Add data rows
        for idx, row in df.iterrows():
            values = [row[col] for col in columns]
            self.tree.insert("", tk.END, values=values, tags=(str(idx),))

    def clear_treeview(self):
        """Clear all data from the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree["columns"] = []
        self.tree["show"] = "tree"

    def sort_column(self, col: str):
        """Sort the treeview by the specified column."""
        if not self.table_data is None:
            # Toggle sort order
            if hasattr(self, '_sort_reverse'):
                self._sort_reverse = not self._sort_reverse
            else:
                self._sort_reverse = False

            # Sort dataframe
            self.table_data = self.table_data.sort_values(col, ascending=not self._sort_reverse)

            # Reload treeview
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            self.update_treeview(column_names, self.table_data)

    def create_record(self):
        """Create a new record in the current table."""
        if not self.current_table or not self.conn:
            messagebox.showwarning("Warning", "Please select a table first.")
            return

        # Get column information
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = cursor.fetchall()

        # Create input dialog
        self.show_record_dialog("Create Record", columns, None)

    def update_record(self):
        """Update the selected record."""
        if not self.current_table or not self.conn:
            messagebox.showwarning("Warning", "Please select a table first.")
            return

        # Get selected item
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to update.")
            return

        # Get column information
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = cursor.fetchall()

        # Get current values
        item = self.tree.item(selection[0])
        current_values = item['values']

        # Create input dialog
        self.show_record_dialog("Update Record", columns, current_values)

    def delete_record(self):
        """Delete the selected record."""
        if not self.current_table or not self.conn:
            messagebox.showwarning("Warning", "Please select a table first.")
            return

        # Get selected item
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record to delete.")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            return

        try:
            # Get primary key (assuming first column is primary key)
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = cursor.fetchall()
            pk_column = columns[0][1]  # First column name

            item = self.tree.item(selection[0])
            pk_value = item['values'][0]

            # Delete record
            cursor.execute(f"DELETE FROM {self.current_table} WHERE {pk_column} = ?", (pk_value,))
            self.conn.commit()

            # Refresh table
            self.refresh_table()
            self.status_var.set("Record deleted successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record:\n{str(e)}")

    def refresh_table(self):
        """Refresh the current table data."""
        if self.current_table:
            self.load_table_data(self.current_table)

    def show_record_dialog(self, title: str, columns: List, current_values: Optional[List] = None):
        """Show a dialog for creating/updating records."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create form fields
        entries = {}
        for i, col in enumerate(columns):
            col_name, col_type = col[1], col[2]

            ttk.Label(dialog, text=f"{col_name}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)

            if col_type.upper() in ['TEXT', 'VARCHAR', 'CHAR']:
                entry = ttk.Entry(dialog, width=30)
            else:
                entry = ttk.Entry(dialog, width=30)

            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)

            # Set current value if updating
            if current_values and i < len(current_values):
                entry.insert(0, str(current_values[i]) if current_values[i] is not None else "")

            entries[col_name] = entry

        dialog.columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=len(columns), column=0, columnspan=2, pady=10)

        def save_record():
            try:
                # Collect values
                values = []
                placeholders = []
                for col in columns:
                    col_name = col[1]
                    value = entries[col_name].get()
                    values.append(value)
                    placeholders.append("?")

                if title == "Create Record":
                    # INSERT
                    sql = f"INSERT INTO {self.current_table} VALUES ({', '.join(placeholders)})"
                    cursor = self.conn.cursor()
                    cursor.execute(sql, values)
                else:
                    # UPDATE
                    set_clause = ", ".join([f"{col[1]} = ?" for col in columns[1:]])  # Skip first column (PK)
                    sql = f"UPDATE {self.current_table} SET {set_clause} WHERE {columns[0][1]} = ?"
                    cursor = self.conn.cursor()
                    cursor.execute(sql, values[1:] + [values[0]])  # PK value at end

                self.conn.commit()
                dialog.destroy()
                self.refresh_table()
                self.status_var.set(f"Record {'created' if title == 'Create Record' else 'updated'} successfully")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save record:\n{str(e)}")

        ttk.Button(button_frame, text="Save", command=save_record).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).grid(row=0, column=1)

        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = SQLiteCRUDApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()