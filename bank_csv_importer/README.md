# Bank CSV Importer

A Python console application for importing and validating bank CSV files. Supports multiple bank formats and provides data validation, summary statistics, and export capabilities.

## Features

- **CSV Import**: Load bank statement CSV files with automatic bank detection
- **Data Validation**: Validate columns, data types, dates, and amounts
- **Multiple Formats**: Support for generic and bank-specific CSV formats
- **Summary Statistics**: View transaction counts, date ranges, and totals
- **Data Preview**: Display imported data in a formatted table
- **Export**: Convert CSV data to JSON format
- **CLI Interface**: Easy-to-use command-line interface with Click

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd bank_csv_importer
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

### Import and display a CSV file

```bash
python main.py import_csv data.csv
```

### Validate and show summary

```bash
python main.py import_csv data.csv --validate --summary
```

### Save to SQLite database

```bash
python main.py import_csv data.csv --categorize --save-db --db-path bank_transactions.db
```

### Specify bank type

```bash
python main.py import_csv data.csv --bank chase
```

### Display more rows

```bash
python main.py import_csv data.csv --rows 20
```

### Export to JSON

```bash
python main.py export_json data.csv --output data.json
```

### Create a sample CSV file

```bash
python main.py sample
```

This creates a `sample_bank_transactions.csv` file for testing.

## CSV Format

Your CSV file should include these columns (exact names may vary):

| Field | Possible Column Names |
|-------|---------------------|
| Date | `Date`, `date`, `DATE`, `Transaction Date` |
| Description | `Description`, `description`, `DESCRIPTION`, `Memo` |
| Amount | `Amount`, `amount`, `AMOUNT`, `Transaction Amount` |
| Balance | `Balance`, `balance`, `BALANCE` (optional) |
| Type | `Type`, `type`, `TYPE`, `Transaction Type` (optional) |

## Example CSV Format

```csv
Date,Description,Amount,Balance,Type
2024-01-15,Direct Deposit,2500.00,5230.45,Credit
2024-01-14,Coffee Shop,-8.50,2730.45,Debit
2024-01-13,Gas Station,-45.00,2738.95,Debit
```

## Testing

Run the test suite:

```bash
python -m unittest tests.test_importer
```

## Project Structure

```
bank_csv_importer/
├── src/
│   ├── __init__.py
│   ├── importer.py          # Core import logic
│   └── cli.py               # Command-line interface
├── tests/
│   └── test_importer.py     # Unit tests
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Requirements

- Python 3.8+
- pandas: Data manipulation and CSV reading
- click: Command-line interface framework
- tabulate: Pretty-print tabular data

## Supported Banks

Currently supports:
- Generic CSV format
- Chase
- Bank of America
- Wells Fargo

(More bank formats can be easily added)

## Adding New Bank Formats

To add support for a new bank:

1. **Add column mappings** in `src/importer.py`:
   ```python
   COLUMN_MAPPINGS = {
       'your_bank': {
           'date': ['Transaction Date', 'Date'],
           'description': ['Description', 'Payee'],
           'amount': ['Amount', 'Debit', 'Credit'],
           'balance': ['Balance'],
           'type': ['Type']
       }
   }
   ```

2. **Test with sample data**:
   ```bash
   python main.py import-csv your_sample.csv --bank your_bank --categorize
   ```

3. **Update CLI help** if needed (the bank option already accepts custom names)

### Bank-Specific Column Examples

- **Chase**: `Transaction Date`, `Posting Date`, `Description`, `Amount`, `Balance`, `Type`
- **Bank of America**: `Date`, `Description`, `Amount`, `Running Bal.`
- **Wells Fargo**: `Date`, `Description`, `Amount`, `Balance`

## Troubleshooting

### "File not found"
Ensure the CSV file path is correct and the file exists.

### "Required column not found"
Check that your CSV has the required columns (Date, Description, Amount). Column names are case-sensitive but the importer checks multiple common variations.

### Invalid dates/amounts warnings
These indicate rows with data that doesn't match the expected format. Review those rows manually.

## Future Enhancements

- [ ] Support for more bank-specific formats
- [ ] Data filtering and searching capabilities
- [ ] Export to multiple formats (Excel, PDF, etc.)
- [ ] Duplicate transaction detection
- [ ] Category tagging and reporting
- [ ] Database integration for persistent storage
- [ ] GUI interface

## License

MIT
