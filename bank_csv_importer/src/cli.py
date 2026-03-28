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
@click.option('--bank', default='generic', help='Bank type (generic, chase, bofa, wells_fargo)')
@click.option('--validate', is_flag=True, help='Validate data after import')
@click.option('--summary', is_flag=True, help='Show summary statistics')
@click.option('--rows', default=10, help='Number of rows to display')
def import_csv(filepath: str, bank: str, validate: bool, summary: bool, rows: int):
    """Import a bank CSV file."""
    
    try:
        click.echo(f"Importing CSV from: {filepath}")
        
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
def sample():
    """Create a sample CSV file for testing."""
    
    sample_data = """Date,Description,Amount,Balance,Type
2024-01-15,Direct Deposit,2500.00,5230.45,Credit
2024-01-14,Coffee Shop,-8.50,2730.45,Debit
2024-01-14,Gas Station,-45.00,2738.95,Debit
2024-01-13,Paycheck,2500.00,2783.95,Credit
2024-01-12,Grocery Store,-125.30,283.95,Debit
2024-01-11,ATM Withdrawal,-200.00,409.25,Debit
2024-01-10,Transfer In,500.00,609.25,Credit
2024-01-09,Online Purchase,-89.99,109.25,Debit
2024-01-08,Restaurant,-45.60,199.24,Debit
2024-01-07,Pharmacy,-32.15,244.84,Debit
"""
    
    sample_path = Path("sample_bank_transactions.csv")
    sample_path.write_text(sample_data)
    
    click.secho(f"✓ Sample CSV created: {sample_path}", fg='green')
    click.echo("\nYou can now test with:")
    click.echo(f"  python -m src.cli import_csv {sample_path}")


if __name__ == '__main__':
    cli()
