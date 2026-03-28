"""CSV import functionality for bank statements."""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from tabulate import tabulate


class BankCSVImporter:
    """Import and validate bank CSV files."""
    
    # Common bank CSV column mappings
    COLUMN_MAPPINGS = {
        'generic': {
            'date': ['Date', 'date', 'DATE', 'Transaction Date'],
            'description': ['Description', 'description', 'DESCRIPTION', 'Memo', 'memo'],
            'amount': ['Amount', 'amount', 'AMOUNT', 'Transaction Amount'],
            'balance': ['Balance', 'balance', 'BALANCE', 'Account Balance'],
            'type': ['Type', 'type', 'TYPE', 'Transaction Type']
        }
    }
    
    def __init__(self, file_path: str, bank_type: str = 'generic'):
        """
        Initialize the importer.
        
        Args:
            file_path: Path to the CSV file
            bank_type: Type of bank (generic, chase, bofa, wells_fargo, etc.)
        """
        self.file_path = Path(file_path)
        self.bank_type = bank_type
        self.df: Optional[pd.DataFrame] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def import_file(self) -> bool:
        """
        Import the CSV file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.file_path.exists():
                self.errors.append(f"File not found: {self.file_path}")
                return False
                
            if not self.file_path.suffix.lower() == '.csv':
                self.errors.append("File must be a CSV file (.csv)")
                return False
            
            self.df = pd.read_csv(self.file_path)
            
            if self.df.empty:
                self.errors.append("CSV file is empty")
                return False
                
            return True
            
        except Exception as e:
            self.errors.append(f"Error reading CSV file: {str(e)}")
            return False
    
    def validate_columns(self) -> bool:
        """
        Validate that required columns exist.
        
        Returns:
            True if validation passed, False otherwise
        """
        if self.df is None:
            self.errors.append("No data loaded. Call import_file() first.")
            return False
        
        columns = list(self.df.columns)
        mappings = self.COLUMN_MAPPINGS.get(self.bank_type, self.COLUMN_MAPPINGS['generic'])
        
        required_fields = ['date', 'description', 'amount']
        found_columns = {}
        
        for field in required_fields:
            possible_columns = mappings.get(field, [field])
            found = False
            
            for col in possible_columns:
                if col in columns:
                    found_columns[field] = col
                    found = True
                    break
            
            if not found:
                self.errors.append(
                    f"Required column '{field}' not found. "
                    f"Expected one of: {', '.join(possible_columns)}"
                )
                return False
        
        self.found_columns = found_columns
        return True
    
    def validate_data(self) -> bool:
        """
        Validate data types and values.
        
        Returns:
            True if validation passed, False otherwise
        """
        if self.df is None:
            self.errors.append("No data loaded.")
            return False
        
        if not hasattr(self, 'found_columns'):
            self.errors.append("Columns not validated. Call validate_columns() first.")
            return False
        
        date_col = self.found_columns['date']
        amount_col = self.found_columns['amount']
        
        # Validate dates
        invalid_dates = 0
        for idx, value in enumerate(self.df[date_col]):
            try:
                pd.to_datetime(value)
            except:
                invalid_dates += 1
        
        if invalid_dates > 0:
            self.warnings.append(f"{invalid_dates} invalid date(s) found")
        
        # Validate amounts
        invalid_amounts = 0
        for idx, value in enumerate(self.df[amount_col]):
            try:
                float(value)
            except:
                invalid_amounts += 1
        
        if invalid_amounts > 0:
            self.warnings.append(f"{invalid_amounts} invalid amount(s) found")
        
        return len(self.errors) == 0
    
    def get_summary(self) -> Dict:
        """Get summary statistics of the imported data."""
        if self.df is None:
            return {}
        
        summary = {
            'total_rows': len(self.df),
            'columns': list(self.df.columns),
            'date_range': None,
            'transaction_count': len(self.df)
        }
        
        if hasattr(self, 'found_columns'):
            date_col = self.found_columns.get('date')
            amount_col = self.found_columns.get('amount')
            
            if date_col and amount_col:
                try:
                    dates = pd.to_datetime(self.df[date_col], errors='coerce')
                    valid_dates = dates.dropna()
                    
                    if len(valid_dates) > 0:
                        summary['date_range'] = {
                            'start': str(valid_dates.min()),
                            'end': str(valid_dates.max())
                        }
                    
                    amounts = pd.to_numeric(self.df[amount_col], errors='coerce')
                    valid_amounts = amounts.dropna()
                    
                    if len(valid_amounts) > 0:
                        summary['total_amount'] = float(valid_amounts.sum())
                except:
                    pass
        
        return summary
    
    def display_data(self, max_rows: int = 10) -> None:
        """Display the imported data in a formatted table."""
        if self.df is None:
            print("No data loaded.")
            return
        
        display_df = self.df.head(max_rows)
        print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))
        
        if len(self.df) > max_rows:
            print(f"\n... and {len(self.df) - max_rows} more rows")
