"""Command-line interface for the Bank CSV Importer."""

import click
from pathlib import Path
from .importer import BankCSVImporter
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Bank CSV Importer - Import and validate bank CSV files."""
    pass


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--bank', default='generic', help='Bank type (generic, chase, bofa, wells_fargo, psecu, or custom name)')
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
@click.option('--bank', default='generic', help='Bank type (generic, chase, bofa, wells_fargo, psecu, or custom name)')
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
def gui():
    """Launch the graphical user interface."""
    launch_gui()


def launch_gui():
    """Launch the GUI application."""
    root = tk.Tk()
    root.title("Bank CSV Importer")
    root.geometry("800x600")
    
    # Variables
    filepath_var = tk.StringVar()
    bank_var = tk.StringVar(value="generic")
    validate_var = tk.BooleanVar()
    categorize_var = tk.BooleanVar()
    summary_var = tk.BooleanVar()
    save_db_var = tk.BooleanVar()
    notes_var = tk.BooleanVar()
    db_path_var = tk.StringVar(value="transactions.db")
    rows_var = tk.StringVar(value="20")
    
    # File selection
    tk.Label(root, text="CSV File:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    tk.Entry(root, textvariable=filepath_var, width=50).grid(row=0, column=1, padx=10, pady=5)
    tk.Button(root, text="Browse", command=lambda: browse_file(filepath_var)).grid(row=0, column=2, padx=10, pady=5)
    
    # Bank type
    tk.Label(root, text="Bank Type:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    bank_options = ["generic", "chase", "bofa", "wells_fargo", "psecu"]
    tk.OptionMenu(root, bank_var, *bank_options).grid(row=1, column=1, sticky="w", padx=10, pady=5)
    
    # Options
    tk.Checkbutton(root, text="Validate Data", variable=validate_var).grid(row=2, column=0, sticky="w", padx=10, pady=5)
    tk.Checkbutton(root, text="Categorize Transactions", variable=categorize_var).grid(row=2, column=1, sticky="w", padx=10, pady=5)
    tk.Checkbutton(root, text="Show Summary", variable=summary_var).grid(row=3, column=0, sticky="w", padx=10, pady=5)
    tk.Checkbutton(root, text="Assign Notes", variable=notes_var).grid(row=3, column=1, sticky="w", padx=10, pady=5)
    tk.Checkbutton(root, text="Save to Database", variable=save_db_var).grid(row=4, column=0, sticky="w", padx=10, pady=5)
    
    # DB path
    tk.Label(root, text="Database Path:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
    tk.Entry(root, textvariable=db_path_var, width=50).grid(row=5, column=1, padx=10, pady=5)
    
    # Rows
    tk.Label(root, text="Display Rows:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
    tk.Entry(root, textvariable=rows_var, width=10).grid(row=6, column=1, sticky="w", padx=10, pady=5)
    
    # Import button
    import_button = tk.Button(root, text="Import CSV", command=lambda: import_csv_gui(
        filepath_var.get(), bank_var.get(), validate_var.get(), categorize_var.get(),
        summary_var.get(), save_db_var.get(), notes_var.get(), db_path_var.get(),
        int(rows_var.get()) if rows_var.get().isdigit() else 20, output_text
    ))
    import_button.grid(row=7, column=0, columnspan=3, pady=10)
    
    # Output text area
    output_text = scrolledtext.ScrolledText(root, width=90, height=20)
    output_text.grid(row=8, column=0, columnspan=3, padx=10, pady=10)
    
    root.mainloop()


def browse_file(filepath_var):
    """Browse for a CSV file."""
    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if filename:
        filepath_var.set(filename)


def import_csv_gui(filepath, bank, validate, categorize, summary, save_db, notes, db_path, rows, output_text):
    """Import CSV using GUI - runs in a separate thread to avoid freezing the GUI."""
    def run_import():
        try:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, f"Importing CSV from: {filepath}\n")
            
            importer = BankCSVImporter(filepath, bank_type=bank)
            
            # Import the file
            if not importer.import_file():
                output_text.insert(tk.END, "✗ Failed to import file:\n")
                for error in importer.errors:
                    output_text.insert(tk.END, f"  - {error}\n")
                return
            
            output_text.insert(tk.END, "✓ File imported successfully\n")
            output_text.insert(tk.END, f"  Rows: {len(importer.df)}, Columns: {len(importer.df.columns)}\n")
            
            # Validate columns
            if validate or summary:
                if not importer.validate_columns():
                    output_text.insert(tk.END, "✗ Column validation failed:\n")
                    for error in importer.errors:
                        output_text.insert(tk.END, f"  - {error}\n")
                    return
                
                output_text.insert(tk.END, "✓ Columns validated\n")
                
                # Validate data
                if not importer.validate_data():
                    output_text.insert(tk.END, "✗ Data validation failed:\n")
                    for error in importer.errors:
                        output_text.insert(tk.END, f"  - {error}\n")
                    return
                
                if importer.warnings:
                    output_text.insert(tk.END, "⚠ Warnings:\n")
                    for warning in importer.warnings:
                        output_text.insert(tk.END, f"  - {warning}\n")
                
                output_text.insert(tk.END, "✓ Data validated\n")
            
            # Categorize transactions
            if categorize or summary:
                if not importer.categorize_transactions():
                    output_text.insert(tk.END, "✗ Categorization failed:\n")
                    for error in importer.errors:
                        output_text.insert(tk.END, f"  - {error}\n")
                    return
                
                output_text.insert(tk.END, "✓ Transactions categorized\n")
            
            # Assign notes
            if notes or summary:
                if not importer.assign_notes():
                    output_text.insert(tk.END, "✗ Note assignment failed:\n")
                    for error in importer.errors:
                        output_text.insert(tk.END, f"  - {error}\n")
                    return
                
                output_text.insert(tk.END, "✓ Notes assigned\n")
            
            # Display data
            output_text.insert(tk.END, "\nData Preview:\n")
            output_text.insert(tk.END, "-" * 80 + "\n")
            # Get the display string
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            importer.display_data(max_rows=rows)
            sys.stdout = old_stdout
            output_text.insert(tk.END, buffer.getvalue())
            
            # Show summary
            if summary:
                output_text.insert(tk.END, "\nSummary Statistics:\n")
                output_text.insert(tk.END, "-" * 80 + "\n")
                summary_data = importer.get_summary()
                
                for key, value in summary_data.items():
                    if isinstance(value, dict):
                        output_text.insert(tk.END, f"{key}:\n")
                        for k, v in value.items():
                            output_text.insert(tk.END, f"  {k}: {v}\n")
                    elif isinstance(value, list):
                        output_text.insert(tk.END, f"{key}: {', '.join(map(str, value[:5]))}\n")
                        if len(value) > 5:
                            output_text.insert(tk.END, f"  ... and {len(value) - 5} more\n")
                    else:
                        output_text.insert(tk.END, f"{key}: {value}\n")
            
            if save_db:
                inserted = importer.save_to_sqlite(db_path=db_path)
                if inserted > 0:
                    output_text.insert(tk.END, f"✓ Saved {inserted} new transaction(s) to database: {db_path}\n")
                else:
                    if importer.errors:
                        output_text.insert(tk.END, "✗ Save to database failed:\n")
                        for error in importer.errors:
                            output_text.insert(tk.END, f"  - {error}\n")
                    else:
                        output_text.insert(tk.END, "✓ No new transactions to save (duplicates skipped).\n")
        
        except Exception as e:
            output_text.insert(tk.END, f"✗ Error: {str(e)}\n")
    
    # Run in a separate thread to avoid freezing the GUI
    threading.Thread(target=run_import, daemon=True).start()


if __name__ == '__main__':
    cli()
