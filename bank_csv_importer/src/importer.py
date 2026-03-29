"""CSV import functionality for bank statements."""

import pandas as pd
import sqlite3
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
        },
        'chase': {
            'date': ['Transaction Date', 'Posting Date'],
            'description': ['Description', 'Memo'],
            'amount': ['Amount'],
            'balance': ['Balance'],
            'type': ['Type']
        },
        'bofa': {
            'date': ['Date'],
            'description': ['Description', 'Payee'],
            'amount': ['Amount', 'Debit', 'Credit'],
            'balance': ['Running Bal.'],
            'type': ['Type']
        },
        'wells_fargo': {
            'date': ['Date'],
            'description': ['Description', 'Payee'],
            'amount': ['Amount'],
            'balance': ['Balance'],
            'type': ['Type']
        },
        'psecu': {
        'date': ['Transaction Date', 'Date', 'Posting Date'],
        'description': ['Transaction Description', 'Payee', 'Memo'], 
        'amount': ['Amount', 'Debit', 'Credit'],
        'balance': ['Balance', 'Running Bal.'],
        'type': ['Type', 'Transaction Type','Category'],
        'note': ['Note', 'Notes', 'Check/Misc']
    },
    }
    
    # Transaction category mappings based on description patterns
    CATEGORY_MAPPINGS = {
        'Income': [
            'direct deposit', 'payroll', 'salary', 'deposit', 'transfer in',
            'income', 'wage', 'paycheck', 'refund', 'rebate', 'bonus'
        ],
        'Groceries': [
            'grocery', 'supermarket', 'whole foods', 'safeway', 'kroger',
            'walmart', 'target', 'costco', 'trader joe', 'publix', 'meijer'
        ],
        'Dining': [
            'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'burger king',
            'subway', 'pizza', 'taco', 'chinese', 'italian', 'mexican', 'thai'
        ],
        'Transportation': [
            'gas', 'fuel', 'shell', 'chevron', 'exxon', 'bp', 'mobil',
            'uber', 'lyft', 'taxi', 'parking', 'toll', 'transit', 'bus', 'train'
        ],
        'Entertainment': [
            'netflix', 'spotify', 'amazon prime', 'hulu', 'disney', 'movie',
            'theater', 'concert', 'game', 'steam', 'playstation', 'xbox'
        ],
        'Utilities': [
            'electric', 'power', 'gas utility', 'water', 'sewer', 'internet',
            'cable', 'phone', 'mobile', 'verizon', 'att', 'tmobile', 'comcast'
        ],
        'Healthcare': [
            'pharmacy', 'doctor', 'hospital', 'dental', 'medical', 'cvs',
            'walgreens', 'rite aid', 'kaiser', 'anthem', 'blue cross'
        ],
        'Shopping': [
            'amazon', 'ebay', 'etsy', 'best buy', 'home depot', 'lowes',
            'ikea', 'macy', 'nordstrom', 'clothing', 'shoes', 'jewelry'
        ],
        'Bills & Payments': [
            'payment', 'bill pay', 'auto pay', 'insurance', 'mortgage',
            'rent', 'loan', 'credit card', 'minimum payment'
        ],
        'ATM & Cash': [
            'atm', 'withdrawal', 'cash', 'check', 'money order'
        ],
        'Fees': [
            'fee', 'charge', 'penalty', 'overdraft', 'service charge',
            'monthly fee', 'annual fee', 'late fee'
        ],
        'Transfers': [
            'transfer', 'wire', 'ach', 'internal transfer', 'between accounts'
        ]
    }
    
    # Transaction category mappings based on description patterns
    CATEGORY_MAPPINGS_MINE = {
        'Income': [
            'direct deposit', 'payroll', 'salary', 'deposit', 'transfer in',
            'income', 'wage', 'paycheck', 'refund', 'rebate', 'bonus','pershing'
        ],
        'Groceries': [
            'grocery', 'supermarket', 'whole foods', 'safeway', 'kroger',
            'walmart', 'target', 'costco', 'trader joe', 'publix', 'meijer'
        ],
        'Dining': [
            'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'burger king',
            'subway', 'pizza', 'taco', 'chinese', 'italian', 'mexican', 'thai'
        ],
        'Transportation': [
            'gas', 'fuel', 'shell', 'chevron', 'exxon', 'bp', 'mobil',
            'uber', 'lyft', 'taxi', 'parking', 'toll', 'transit', 'bus', 'train'
        ],
        'Entertainment': [
            'netflix', 'spotify', 'amazon prime', 'hulu', 'disney', 'movie',
            'theater', 'concert', 'game', 'steam', 'playstation', 'xbox',
            'peacock', 'paramount', 'apple tv', 'vudu', 'fandango'
        ],
        'Utilities': [
            'electric', 'power', 'gas utility', 'sewer', 'internet','ppl', 'veolia',
            'cable', 'phone', 'mobile', 'verizon', 'att', 'tmobile', 'comcast'
        ],
        'Healthcare': [
            'pharmacy', 'doctor', 'hospital', 'dental', 'medical', 'cvs',
            'walgreens', 'rite aid', 'kaiser', 'anthem', 'blue cross'
        ],
        'Shopping': [
            'amazon', 'ebay', 'etsy', 'best buy', 'home depot', 'lowes',
            'ikea', 'macy', 'nordstrom', 'clothing', 'shoes', 'jewelry'
        ],
        'Bills & Payments': [
            'payment', 'bill pay', 'auto pay', 'insurance', 'mortgage',
            'rent', 'loan', 'credit card', 'minimum payment'
        ],
        'ATM & Cash': [
            'atm', 'withdrawal', 'cash', 'check', 'money order'
        ],
        'Fees': [
            'fee', 'charge', 'penalty', 'overdraft', 'service charge',
            'monthly fee', 'annual fee', 'late fee'
        ],
        'Transfers': [
            'transfer', 'wire', 'ach', 'internal transfer', 'between accounts'
        ],
        'Charitable Giving': [
            'charity', 'donation', 'nonprofit', 'fundraiser', 'cause', 'ngo', 
            'red cross', 'unicef', 'salvation army','livingwatercommu'
        ],
        'Investments': [
            'investment', 'brokerage', 'stock', 'mutual fund', 'robin',
            'fidelity', 'vanguard', 'etrade', 'schwab', 'td ameritrade',
            'guardian', 'merrill', 'charles schwab', 'fidelity investments'

        ],
        'trash/sewer': [
            'trash', 'sewer', 'waste management', 'garbage', 'recycling', 
            'penn waste', 'allied waste',  'wm'
            ]
    }

    def __init__(self, file_path: str, bank_type: str = 'generic'):
        """
        Initialize the importer.
        
        Args:
            file_path: Path to the CSV file
            bank_type: Type of bank (generic, chase, bofa, wells_fargo, psecu, etc.)
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
            print (f"Attempting to import file: {self.file_path} [Bank type: {self.bank_type}]")
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
        #print (f"Validating columns for bank type: {self.bank_type}")
        columns = list(self.df.columns)
        mappings = self.COLUMN_MAPPINGS.get(self.bank_type, self.COLUMN_MAPPINGS['generic'])
        
        required_fields = ['date', 'description', 'amount', 'balance', 'type']
        found_columns = {}
        
        for field in required_fields:
            print (f"Looking for column for field '{field}' among possible names: {mappings.get(field, [field])}")
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
    
    def categorize_transactions(self) -> bool:
        """
        Add category column based on transaction descriptions.
        
        Returns:
            True if categorization completed, False otherwise
        """
        print (f"Categorizing transactions based on descriptions using bank type: {self.bank_type}")
        if self.df is None:
            self.errors.append("No data loaded.")
            return False
        
        if not hasattr(self, 'found_columns'):
            self.errors.append("Columns not validated. Call validate_columns() first.")
            return False
              
        desc_col = self.found_columns['description']
        def get_category(description: str) -> str:
            """Get category for a transaction description."""
            if not isinstance(description, str):
                return 'Other'
            
            desc_lower = description.lower()
            
            for category, keywords in self.CATEGORY_MAPPINGS_MINE.items():
                for keyword in keywords:
                    if keyword.lower() in desc_lower:
                        print (f"Categorizing '{description}' as '{category}' based on keyword '{keyword}'")
                        return category
            
            return 'Other'
        
        self.df['Category'] = self.df[desc_col].apply(get_category)
        return True

    def assign_notes(self, note_assignments: Dict[str, str] = None) -> bool:
        """
        Assign notes to transactions based on description patterns or custom assignments.
        
        Args:
            note_assignments: Dict mapping description patterns to note values
            
        Returns:
            True if notes assigned successfully, False otherwise
        """
        if self.df is None:
            self.errors.append("No data loaded.")
            return False
        
        if not hasattr(self, 'found_columns'):
            self.errors.append("Columns not validated. Call validate_columns() first.")
            return False
        
        # Check for pre-existing note column
        existing_note_col = None
        possible_note_cols = ['Note', 'note', 'Notes', 'notes', 'Memo', 'memo', 'Comments', 'comments']
        
        for col in possible_note_cols:
            if col in self.df.columns:
                existing_note_col = col
                self.warnings.append(f"Found existing note column: '{col}'. Pre-existing notes will be preserved.")
                break
        
        desc_col = self.found_columns['description']
        
        # Default note assignments based on common patterns
        default_notes = {
            'atm': 'ATM withdrawal',
            'withdrawal': 'Cash withdrawal',
            'check': 'Check payment',
            'transfer': 'Account transfer',
            'fee': 'Bank fee',
            'interest': 'Interest payment',
            'direct deposit': 'Direct deposit',
            'payroll': 'Payroll deposit',
            'payment': 'Bill payment',
            'refund': 'Refund received'
        }
        
        # Merge with user-provided assignments
        if note_assignments:
            default_notes.update(note_assignments)
        
        def get_note(description: str, existing_note: str = '') -> str:
            """Get note for a transaction description."""
            # If pre-existing note exists and is not empty, preserve it
            if existing_note and isinstance(existing_note, str) and existing_note.strip():
                return existing_note
            
            if not isinstance(description, str):
                return ''
            
            desc_lower = description.lower()
            
            # Check for exact pattern matches (order matters - check specific before general)
            for pattern in sorted(default_notes.keys(), key=len, reverse=True):
                if pattern.lower() in desc_lower:
                    return default_notes[pattern]
            
            return ''
        
        # Create Note column with pre-existing data preserved
        if existing_note_col:
            self.df['Note'] = self.df.apply(
                lambda row: get_note(row[desc_col], row.get(existing_note_col, '')),
                axis=1
            )
        else:
            self.df['Note'] = self.df[desc_col].apply(get_note)
        
        return True

    def save_to_sqlite(self, db_path: str = 'transactions.db', table_name: str = 'transactions') -> int:
        """Save imported transactions to SQLite avoiding duplicate inserts."""
        if self.df is None:
            self.errors.append("No data loaded.")
            return 0

        if not hasattr(self, 'found_columns'):
            self.errors.append("Columns not validated. Call validate_columns() first.")
            return 0

        date_col = self.found_columns.get('date')
        desc_col = self.found_columns.get('description')
        amount_col = self.found_columns.get('amount')
        balance_col = self.found_columns.get('balance')
        type_col = self.found_columns.get('type')
        note_col = self.found_columns.get('note') if hasattr(self, 'found_columns') else None


        # Normalize to specific columns names for DB
        db_df = self.df.copy()
        rename_map = {}
        if date_col:
            rename_map[date_col] = 'date'
        if desc_col:
            rename_map[desc_col] = 'description'
        if amount_col:
            rename_map[amount_col] = 'amount'
        if balance_col:
            rename_map[balance_col] = 'balance'
        if type_col:
            rename_map[type_col] = 'type'
        if note_col:
            rename_map[note_col] = 'note'

        db_df = db_df.rename(columns=rename_map)

        # Also rename Note column to note for consistency
        if 'Note' in db_df.columns and 'note' not in db_df.columns:
            db_df = db_df.rename(columns={'Note': 'note'})

        if 'Category' not in db_df.columns:
            db_df['Category'] = 'Other'
        
        if 'Note' not in db_df.columns:
            db_df['Note'] = ''

        required_db_cols = ['date', 'description', 'amount', 'balance', 'type']
        for col in required_db_cols:
            if col not in db_df.columns:
                db_df[col] = None

        conn = sqlite3.connect(db_path)
        try:
            c = conn.cursor()
            c.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    description TEXT,
                    amount REAL,
                    balance REAL,
                    type TEXT,
                    note TEXT,
                    category TEXT,
                    UNIQUE(date, description, amount, type)
                )
            """)
            conn.commit()

            inserted = 0
            for _, row in db_df.iterrows():
                row_date = None
                if pd.notna(row['date']):
                    try:
                        row_date = pd.to_datetime(row['date'], errors='coerce')
                        if pd.notna(row_date):
                            row_date = row_date.isoformat()
                        else:
                            row_date = str(row['date'])
                    except Exception:
                        row_date = str(row['date'])
                row_description = str(row['description']) if pd.notna(row['description']) else None
                row_amount = None
                try:
                    row_amount = float(row['amount']) if pd.notna(row['amount']) else None
                except Exception:
                    row_amount = None
                row_balance = None
                try:
                    row_balance = float(row['balance']) if pd.notna(row['balance']) else None
                except Exception:
                    row_balance = None
                row_type = str(row['type']) if pd.notna(row['type']) else None
                row_category = str(row['Category']) if pd.notna(row['Category']) else None
                row_note = str(row['note']) if 'note' in row and pd.notna(row['note']) else None    
                # Skip very bad rows
                if not row_date or not row_description or row_amount is None:
                    continue
                print (f"Inserting transaction: Date={row_date}, Description='{row_description}', Amount={row_amount}, Type='{row_type}', Note='{row_note}', Category='{row_category}'")   
                c.execute(
                    f"INSERT OR IGNORE INTO {table_name} (date, description, amount, balance, type, note, category) VALUES (?,?,?,?,?,?,?)",
                    (row_date, row_description, row_amount, row_balance, row_type, row_note,row_category),
                )
                inserted += c.rowcount

            conn.commit()
            return inserted

        except Exception as e:
            self.errors.append(f"Error saving to SQLite: {e}")
            return 0

        finally:
            conn.close()

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
        
        # Add category summary if categories exist
        if 'Category' in self.df.columns:
            category_summary = self.df['Category'].value_counts().to_dict()
            summary['categories'] = category_summary
            
            # Category spending summary
            if amount_col:
                try:
                    amounts = pd.to_numeric(self.df[amount_col], errors='coerce')
                    category_spending = {}
                    
                    for category in self.df['Category'].unique():
                        category_amounts = amounts[self.df['Category'] == category]
                        valid_category_amounts = category_amounts.dropna()
                        if len(valid_category_amounts) > 0:
                            category_spending[category] = float(valid_category_amounts.sum())
                    
                    summary['category_spending'] = category_spending
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
