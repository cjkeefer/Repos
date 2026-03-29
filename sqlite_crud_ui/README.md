# SQLite CRUD UI

A modern graphical user interface for performing Create, Read, Update, and Delete operations on SQLite databases. Built with Python and Tkinter for cross-platform compatibility.

## Features

- **Database Connection**: Connect to any SQLite database file (.db)
- **Table Browser**: View all tables in the database
- **Data Viewer**: Display table contents in a sortable, scrollable grid
- **CRUD Operations**:
  - **Create**: Add new records with a user-friendly form
  - **Read**: View all records in a table
  - **Update**: Modify existing records
  - **Delete**: Remove records with confirmation
- **Data Types**: Automatic handling of different SQLite data types
- **Sorting**: Click column headers to sort data
- **Status Updates**: Real-time status information
- **Error Handling**: Comprehensive error messages and validation

## Installation

1. **Navigate to the project directory**:
   ```bash
   cd sqlite_crud_ui
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Launch the Application

```bash
python main.py
```

Or use the launcher script:

```bash
python launch.py
```

### Testing the Application

A sample database (`sample_crud.db`) is included for testing with sample data:

- **users** table: User information (id, name, email, age, created_date)
- **products** table: Product catalog (id, name, price, category, in_stock)

Run the test script:

```bash
python test_crud.py
```

This will test all CRUD operations with the sample database.

### Connecting to a Database

1. Click the "Browse" button to select a SQLite database file (.db)
2. Click "Connect" to establish the connection
3. The application will load and display all tables in the database

### Working with Tables

1. **Select a Table**: Click on any table name in the left panel
2. **View Data**: Table contents will be displayed in the main grid
3. **Sort Data**: Click on column headers to sort by that column
4. **Navigate**: Use scrollbars to view large datasets

### CRUD Operations

#### Create a New Record
1. Select a table from the list
2. Click the "Create" button
3. Fill in the form fields
4. Click "Save"

#### Update an Existing Record
1. Select a table and click on a row in the data grid
2. Click the "Update" button
3. Modify the values in the form
4. Click "Save"

#### Delete a Record
1. Select a table and click on a row in the data grid
2. Click the "Delete" button
3. Confirm the deletion

#### Refresh Data
- Click "Refresh" to reload the current table data

## Requirements

- Python 3.8+
- pandas: Data manipulation and database operations
- tkinter: Built-in Python GUI framework (included with Python)
- sqlite3: Built-in SQLite database support

## Project Structure

```
sqlite_crud_ui/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Supported Data Types

The application automatically handles SQLite data types:
- INTEGER
- REAL (floating point)
- TEXT
- BLOB
- NULL

## Limitations

- Assumes the first column is the primary key for UPDATE/DELETE operations
- Does not support complex SQL queries or joins
- No support for database schema modifications
- Single database connection at a time

## Troubleshooting

### "Database file not found"
- Ensure the .db file exists and you have read/write permissions
- Check the file path for typos

### "No tables found"
- Verify the database contains tables (not just views or indexes)
- Some system tables are hidden for clarity

### "Failed to save record"
- Check data types match the table schema
- Ensure required fields are not empty
- Verify primary key constraints

### GUI doesn't start
- Ensure tkinter is available (usually included with Python)
- Try running `python -c "import tkinter; print('Tkinter available')"`

## Future Enhancements

- [ ] Support for multiple database connections
- [ ] Advanced SQL query builder
- [ ] Export data to CSV/Excel
- [ ] Database schema viewer
- [ ] Batch operations
- [ ] Search and filter functionality
- [ ] Database backup/restore
- [ ] Support for other database types (PostgreSQL, MySQL)

## License

MIT License - feel free to use and modify as needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues or questions, please create an issue in the repository.