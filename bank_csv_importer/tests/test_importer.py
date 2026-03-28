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


if __name__ == '__main__':
    unittest.main()
