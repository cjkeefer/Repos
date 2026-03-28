"""Unit tests for the Bank CSV Importer."""

import unittest
import tempfile
from pathlib import Path
from src.importer import BankCSVImporter


class TestBankCSVImporter(unittest.TestCase):
    """Test cases for BankCSVImporter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_content = """Date,Description,Amount,Balance,Type
2024-01-15,Deposit,1000.00,1500.00,Credit
2024-01-14,Withdrawal,-200.00,500.00,Debit
2024-01-13,Purchase,-45.50,700.00,Debit
"""
        self.csv_path = Path(self.temp_dir) / "test.csv"
        self.csv_path.write_text(self.csv_content)
    
    def test_import_file_success(self):
        """Test successful file import."""
        importer = BankCSVImporter(str(self.csv_path))
        result = importer.import_file()
        
        self.assertTrue(result)
        self.assertIsNotNone(importer.df)
        self.assertEqual(len(importer.df), 3)
    
    def test_import_file_not_found(self):
        """Test import with non-existent file."""
        importer = BankCSVImporter("/nonexistent/path.csv")
        result = importer.import_file()
        
        self.assertFalse(result)
        self.assertTrue(len(importer.errors) > 0)
    
    def test_validate_columns_success(self):
        """Test successful column validation."""
        importer = BankCSVImporter(str(self.csv_path))
        importer.import_file()
        result = importer.validate_columns()
        
        self.assertTrue(result)
    
    def test_validate_columns_missing(self):
        """Test column validation with missing columns."""
        bad_csv_path = Path(self.temp_dir) / "bad.csv"
        bad_csv_path.write_text("Col1,Col2,Col3\n1,2,3")
        
        importer = BankCSVImporter(str(bad_csv_path))
        importer.import_file()
        result = importer.validate_columns()
        
        self.assertFalse(result)
        self.assertTrue(len(importer.errors) > 0)
    
    def test_get_summary(self):
        """Test summary generation."""
        importer = BankCSVImporter(str(self.csv_path))
        importer.import_file()
        importer.validate_columns()
        
        summary = importer.get_summary()
        
        self.assertEqual(summary['total_rows'], 3)
        self.assertIn('total_amount', summary)

    def test_assign_notes(self):
        """Test note assignment functionality."""
        importer = BankCSVImporter(str(self.csv_path))
        importer.import_file()
        importer.validate_columns()
        
        result = importer.assign_notes()
        self.assertTrue(result)
        
        # Check that Note column was added
        self.assertIn('Note', importer.df.columns)
        
        # Check that withdrawal got a note
        withdrawal_row = importer.df[importer.df['Description'] == 'Withdrawal'].iloc[0]
        self.assertIn(withdrawal_row['Note'], ['ATM withdrawal', 'Cash withdrawal'])

    def test_save_to_sqlite_avoids_duplicates(self):
        """Test saving to SQLite and deduplication."""
        importer = BankCSVImporter(str(self.csv_path))
        importer.import_file()
        importer.validate_columns()
        importer.categorize_transactions()

        db_path = Path(self.temp_dir) / 'test_transactions.db'
        inserted_first = importer.save_to_sqlite(str(db_path), table_name='transactions')

        self.assertEqual(inserted_first, 3)

        # Second save should detect duplicates (no new rows inserted)
        inserted_second = importer.save_to_sqlite(str(db_path), table_name='transactions')
        self.assertEqual(inserted_second, 0)

        # Optionally verify table rowcount from database
        import sqlite3
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM transactions')
            count = cursor.fetchone()[0]

        self.assertEqual(count, 3)


if __name__ == '__main__':
    unittest.main()
