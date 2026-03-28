"""Command-line interface for the Bank CSV Importer."""

import click
from pathlib import Path
from .importer import BankCSVImporter
import json


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Bank CSV Importer - Import and validate bank CSV files."""
    pass


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--bank', default='generic', help='Bank type (generic, chase, bofa, wells_fargo, or custom name)')
@click.option('--validate', is_flag=True, help='Validate data after import')
@click.option('--categorize', is_flag=True, help='Categorize transactions based on descriptions')
@click.option('--summary', is_flag=True, help='Show summary statistics')
@click.option('--save-db', is_flag=True, help='Save imported transactions to SQLite database')
@click.option('--notes', is_flag=True, help='Assign notes to transactions based on descriptions')
@click.option('--db-path', default='transactions.db', help='Path to SQLite database file')
@click.option('--rows', default=20, help='Number of rows to display')
def import_csv(filepath: str, bank: str, validate: bool, categorize: bool, summary: bool, save_db: bool, notes: bool, db_path: str, rows: int):
    """Import a bank CSV file."""
    
    try:
        #click.echo(f"Importing CSV from: {filepath}")
        
        importer = BankCSVImporter(filepath, bank_type=bank)
        
        # Import the file
        if not importer.import_file():
            click.secho("✗ Failed to import file:", fg='red', bold=True)
            for error in importer.errors:
                click.echo(f"  - {error}")
            return
        
        click.secho("✓ File imported successfully", fg='green')
        click.echo(f"  Rows: {len(importer.df)}, Columns: {len(importer.df.columns)}")
        
        # Validate columns
        if validate or summary:
            if not importer.validate_columns():
                click.secho("✗ Column validation failed:", fg='red', bold=True)
                for error in importer.errors:
                    click.echo(f"  - {error}")
                return
            
            click.secho("✓ Columns validated", fg='green')
            
            # Validate data
            if not importer.validate_data():
                click.secho("✗ Data validation failed:", fg='red', bold=True)
                for error in importer.errors:
                    click.echo(f"  - {error}")
                return
            
            if importer.warnings:
                click.secho("⚠ Warnings:", fg='yellow')
                for warning in importer.warnings:
                    click.echo(f"  - {warning}")
            
            click.secho("✓ Data validated", fg='green')
        
        # Categorize transactions
        if categorize or summary:
            if not importer.categorize_transactions():
                click.secho("✗ Categorization failed:", fg='red', bold=True)
                for error in importer.errors:
                    click.echo(f"  - {error}")
                return
            
            click.secho("✓ Transactions categorized", fg='green')
        
        # Assign notes
        if notes or summary:
            if not importer.assign_notes():
                click.secho("✗ Note assignment failed:", fg='red', bold=True)
                for error in importer.errors:
                    click.echo(f"  - {error}")
                return
            
            click.secho("✓ Notes assigned", fg='green')
        
        # Display data
        click.echo("\nData Preview:")
        click.echo("-" * 80)
        importer.display_data(max_rows=rows)
        
        # Show summary
        if summary:
            click.echo("\nSummary Statistics:")
            click.echo("-" * 80)
            summary_data = importer.get_summary()
            
            for key, value in summary_data.items():
                if isinstance(value, dict):
                    click.echo(f"{key}:")
                    for k, v in value.items():
                        click.echo(f"  {k}: {v}")
                elif isinstance(value, list):
                    click.echo(f"{key}: {', '.join(map(str, value[:5]))}")
                    if len(value) > 5:
                        click.echo(f"  ... and {len(value) - 5} more")
                else:
                    click.echo(f"{key}: {value}")

        if save_db:
            inserted = importer.save_to_sqlite(db_path=db_path)
            if inserted > 0:
                click.secho(f"✓ Saved {inserted} new transaction(s) to database: {db_path}", fg='green')
            else:
                if importer.errors:
                    click.secho("✗ Save to database failed:", fg='red', bold=True)
                    for error in importer.errors:
                        click.echo(f"  - {error}")
                else:
                    click.secho("✓ No new transactions to save (duplicates skipped).", fg='yellow')

    except Exception as e:
        click.secho(f"✗ Error: {str(e)}", fg='red', bold=True)


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output JSON file path')
def export_json(filepath: str, output: str):
    """Export CSV data to JSON format."""
    
    try:
        click.echo(f"Exporting CSV to JSON: {filepath}")
        
        importer = BankCSVImporter(filepath)
        
        if not importer.import_file():
            click.secho("✗ Failed to import file:", fg='red', bold=True)
            for error in importer.errors:
                click.echo(f"  - {error}")
            return
        
        # Convert to JSON
        json_data = importer.df.to_json(orient='records', indent=2)
        
        if output:
            output_path = Path(output)
            output_path.write_text(json_data)
            click.secho(f"✓ Exported to: {output_path}", fg='green')
        else:
            click.echo(json_data)
    
    except Exception as e:
        click.secho(f"✗ Error: {str(e)}", fg='red', bold=True)


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--bank', default='generic', help='Bank type (generic, chase, bofa, wells_fargo, or custom name)')
@click.option('--output', '-o', type=click.Path(), help='Output file path for notes (optional)')
@click.option('--save-db', is_flag=True, help='Save notes directly to SQLite database')
@click.option('--db-path', default='transactions.db', help='Path to SQLite database file')
def add_notes(filepath: str, bank: str, output: str, save_db: bool, db_path: str):
    """Add notes to transactions based on description patterns."""
    try:
        click.echo(f"Adding notes to transactions from: {filepath}")
        
        importer = BankCSVImporter(filepath, bank_type=bank)
        
        # Import the file
        if not importer.import_file():
            click.secho("✗ Failed to import file:", fg='red', bold=True)
            for error in importer.errors:
                click.echo(f"  - {error}")
            return
        
        click.secho("✓ File imported successfully", fg='green')
        
        # Validate columns
        if not importer.validate_columns():
            click.secho("✗ Column validation failed:", fg='red', bold=True)
            for error in importer.errors:
                click.echo(f"  - {error}")
            return
        
        click.secho("✓ Columns validated", fg='green')
        
        # Assign notes
        if not importer.assign_notes():
            click.secho("✗ Note assignment failed:", fg='red', bold=True)
            for error in importer.errors:
                click.echo(f"  - {error}")
            return
        
        if importer.warnings:
            click.secho("⚠ Warnings:", fg='yellow')
            for warning in importer.warnings:
                click.echo(f"  - {warning}")
        
        click.secho("✓ Notes assigned to transactions", fg='green')
        
        # Display preview with notes
        click.echo("\nTransactions with Notes:")
        click.echo("-" * 80)
        desc_col = importer.found_columns.get('description')
        if desc_col and 'Note' in importer.df.columns:
            click.echo(importer.df[[desc_col, 'Note']].head(15).to_string(index=False))
        
        # Save to output file if specified
        if output:
            output_path = Path(output)
            output_df = importer.df[[desc_col, 'Note']].copy() if desc_col else importer.df[['Note']].copy()
            output_df.to_csv(output_path, index=False)
            click.secho(f"✓ Notes saved to: {output_path}", fg='green')
        
        # Save to database if requested
        if save_db:
            inserted = importer.save_to_sqlite(db_path=db_path)
            if inserted > 0:
                click.secho(f"✓ Saved {inserted} transaction(s) with notes to: {db_path}", fg='green')
            else:
                click.secho("✓ Notes updated in database", fg='green')
    
    except Exception as e:
        click.secho(f"✗ Error: {str(e)}", fg='red', bold=True)


@cli.command()
def sample():
    """Create a sample CSV file for testing."""
    
    sample_data = """Date,Description,Amount,Balance,Type
2024-01-15,Direct Deposit Salary,2500.00,5230.45,Credit
2024-01-14,Starbucks Coffee,-8.50,2730.45,Debit
2024-01-14,Shell Gas Station,-45.00,2738.95,Debit
2024-01-13,Payroll Deposit,2500.00,2783.95,Credit
2024-01-12,Whole Foods Grocery,-125.30,283.95,Debit
2024-01-11,ATM Cash Withdrawal,-200.00,409.25,Debit
2024-01-10,Transfer from Savings,500.00,609.25,Credit
2024-01-09,Amazon Online Purchase,-89.99,109.25,Debit
2024-01-08,Italian Restaurant,-45.60,199.24,Debit
2024-01-07,Walgreens Pharmacy,-32.15,244.84,Debit
2024-01-06,Netflix Subscription,-15.99,212.69,Debit
2024-01-05,Verizon Mobile Bill,-75.00,297.69,Debit
2024-01-04,Home Depot Purchase,-120.50,373.19,Debit
2024-01-03,Doctor Visit Copay,-25.00,398.19,Debit
2024-01-02,Spotify Premium,-9.99,424.18,Debit
2024-01-01,Check Deposit,500.00,434.17,Credit
"""
    
    sample_path = Path("sample_bank_transactions.csv")
    sample_path.write_text(sample_data)
    
    click.secho(f"✓ Sample CSV created: {sample_path}", fg='green')
    click.echo("\nYou can now test with:")
    click.echo(f"  python -m src.cli import_csv {sample_path} --categorize --summary")


if __name__ == '__main__':
    cli()
