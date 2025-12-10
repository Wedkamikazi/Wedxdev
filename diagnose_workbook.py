#!/usr/bin/env python3
"""
Comprehensive diagnostic for Treasury Calendar Workbook
Traces through formulas and data to identify issues
"""

import openpyxl
from openpyxl import load_workbook
from datetime import datetime, timedelta
from collections import defaultdict

print("=" * 80)
print("TREASURY CALENDAR WORKBOOK - COMPREHENSIVE DIAGNOSTIC")
print("=" * 80)

# Load workbook
wb = load_workbook('/home/user/Wedxdev/Treasury_Calendar_Workbook.xlsx', data_only=False)

# ============================================================================
# DIAGNOSTIC 1: Trace source sheet structure and data
# ============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTIC 1: SOURCE SHEET STRUCTURE AND SAMPLE DATA")
print("=" * 80)

source_sheets_config = {
    'SRC_Collections': {'amount_col': 7, 'date_col': 8, 'desc': 'Collections/Revenue'},
    'SRC_OPeX': {'amount_col': 7, 'date_col': 8, 'desc': 'Operating Expenses'},
    'SRC_CAPEX': {'amount_col': 7, 'date_col': 8, 'desc': 'Capital Expenditures'},
    'SRC_HR': {'amount_col': 7, 'date_col': 8, 'desc': 'HR/Payroll'},
    'SRC_Debt': {'amount_col': 8, 'date_col': 9, 'desc': 'Debt Service'},
    'SRC_Fixed': {'amount_col': 7, 'date_col': 8, 'desc': 'Fixed Expenses'},
    'SRC_Variable': {'amount_col': 7, 'date_col': 8, 'desc': 'Variable Expenses'},
    'SRC_Deposits': {'amount_col': 8, 'date_col': 9, 'desc': 'Deposit Maturities'},
}

for sheet_name, config in source_sheets_config.items():
    ws = wb[sheet_name]
    print(f"\n{sheet_name} ({config['desc']}):")
    print("-" * 60)

    # Show header row
    print("  Headers (Row 3):")
    headers = []
    for col in range(1, 12):
        val = ws.cell(row=3, column=col).value
        if val:
            headers.append(f"Col{col}={val}")
    print(f"    {', '.join(headers)}")

    # Show first 3 data rows
    print(f"\n  Sample data (Amount col={config['amount_col']}, Date col={config['date_col']}):")
    for row in range(4, 7):
        amount = ws.cell(row=row, column=config['amount_col']).value
        date = ws.cell(row=row, column=config['date_col']).value
        desc = ws.cell(row=row, column=2).value if ws.cell(row=row, column=2).value else "N/A"

        # Check if amount is formula
        amount_str = str(amount)[:50] if amount else "EMPTY"
        date_str = str(date) if date else "EMPTY"
        date_type = type(date).__name__

        print(f"    Row {row}: Desc={str(desc)[:20]}, Amount={amount_str}, Date={date_str} ({date_type})")

# ============================================================================
# DIAGNOSTIC 2: Check Treasury_Calendar formulas vs source column mapping
# ============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTIC 2: TREASURY CALENDAR FORMULA ANALYSIS")
print("=" * 80)

ws = wb['Treasury_Calendar']

# Show header structure
print("\nHeader structure (Row 1-7, Column A):")
for row in range(1, 9):
    val = ws.cell(row=row, column=1).value
    print(f"  Row {row}: {val}")

# Show date row values
print("\nDate row (Row 6) - First 10 date columns:")
for col in range(4, 14):
    cell = ws.cell(row=6, column=col)
    print(f"  Col {col}: {cell.value} ({type(cell.value).__name__})")

# Show category rows and their formulas
print("\nCategory rows and formulas:")
category_rows = {}
for row in range(8, 35):
    cell_a = ws.cell(row=row, column=1).value
    if cell_a:
        category_rows[row] = cell_a
        # Check first formula column
        formula_cell = ws.cell(row=row, column=4)
        formula = str(formula_cell.value) if formula_cell.value else "EMPTY"
        print(f"  Row {row}: {cell_a}")
        if 'SUMIF' in formula or 'SUM' in formula:
            print(f"         Formula: {formula[:80]}...")

# ============================================================================
# DIAGNOSTIC 3: Validate SUMIF formula references
# ============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTIC 3: SUMIF FORMULA REFERENCE VALIDATION")
print("=" * 80)

# The Treasury Calendar uses SUMIF formulas that should reference:
# =IFERROR(SUMIF(SRC_XXX.$H$4:$H$500,D$6,SRC_XXX.$G$4:$G$500),0)
# Where $H = date column, $G = amount column, D$6 = date in calendar

# Expected column mappings for SUMIF (date_col, amount_col):
expected_sumif_cols = {
    'SRC_Collections': ('H', 'G'),  # H=Date, G=Amount
    'SRC_OPeX': ('H', 'G'),
    'SRC_CAPEX': ('H', 'G'),
    'SRC_HR': ('H', 'G'),
    'SRC_Debt': ('I', 'H'),  # I=Date, H=Amount
    'SRC_Fixed': ('H', 'G'),
    'SRC_Variable': ('H', 'G'),
    'SRC_Deposits': ('I', 'H'),  # I=Date, H=Amount
}

# Check Collections formula
ws = wb['Treasury_Calendar']
for row in range(8, 30):
    cell = ws.cell(row=row, column=4)
    if cell.value and 'SUMIF' in str(cell.value) and 'SRC_Collections' in str(cell.value):
        formula = str(cell.value)
        print(f"\nCollections SUMIF formula (Row {row}):")
        print(f"  {formula}")

        # Parse the formula to check column references
        # Expected: =IFERROR(SUMIF(SRC_Collections.$H$4:$H$500,D$6,SRC_Collections.$G$4:$G$500),0)
        if '$H$' in formula and '$G$' in formula:
            print("  ✓ Column references appear correct (H=date, G=amount)")
        else:
            print("  ✗ Column reference mismatch!")
            print(f"    Expected: H (date), G (amount)")
        break

# ============================================================================
# DIAGNOSTIC 4: Check if dates match between source and calendar
# ============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTIC 4: DATE MATCHING ANALYSIS")
print("=" * 80)

# Get calendar dates
ws = wb['Treasury_Calendar']
calendar_dates = []
for col in range(4, 65):
    date_val = ws.cell(row=6, column=col).value
    if isinstance(date_val, datetime):
        calendar_dates.append(date_val.date())

print(f"Calendar date range: {min(calendar_dates)} to {max(calendar_dates)}")
print(f"Total calendar days: {len(calendar_dates)}")

# Get source sheet dates and check overlap
for sheet_name in ['SRC_Collections', 'SRC_OPeX', 'SRC_CAPEX', 'SRC_HR']:
    ws = wb[sheet_name]
    source_dates = []
    date_col = 8  # Column H
    for row in range(4, 50):
        date_val = ws.cell(row=row, column=date_col).value
        if isinstance(date_val, datetime):
            source_dates.append(date_val.date())

    if source_dates:
        print(f"\n{sheet_name}:")
        print(f"  Date range: {min(source_dates)} to {max(source_dates)}")
        print(f"  Total records with dates: {len(source_dates)}")

        # Check overlap with calendar
        overlap = [d for d in source_dates if d in calendar_dates]
        print(f"  Dates matching calendar: {len(overlap)}")
        if overlap:
            print(f"  Matching dates: {overlap[:5]}{'...' if len(overlap) > 5 else ''}")
        else:
            print("  ⚠️ NO MATCHING DATES! Formulas will return 0")

# ============================================================================
# DIAGNOSTIC 5: Check Payment_Data structure
# ============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTIC 5: PAYMENT_DATA STRUCTURE AND FORMULAS")
print("=" * 80)

ws = wb['Payment_Data']

# Show headers
print("\nPayment_Data Headers (Row 5):")
for col in range(1, 15):
    val = ws.cell(row=5, column=col).value
    if val:
        print(f"  Col {col}: {val}")

# Show sample data
print("\nSample Payment Data:")
for row in range(6, 10):
    payment_id = ws.cell(row=row, column=1).value
    vendor_id = ws.cell(row=row, column=2).value
    amount = ws.cell(row=row, column=8).value
    amount_sar = ws.cell(row=row, column=9).value
    due_date = ws.cell(row=row, column=10).value

    print(f"  Row {row}: ID={payment_id}, Vendor={vendor_id}, Amt={amount}, SAR={str(amount_sar)[:30]}, Date={due_date}")

# ============================================================================
# DIAGNOSTIC 6: Check Payment_Calendar formulas
# ============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTIC 6: PAYMENT_CALENDAR FORMULA ANALYSIS")
print("=" * 80)

ws = wb['Payment_Calendar']

# Show structure
print("\nPayment_Calendar Header Structure:")
for row in range(1, 9):
    for col in range(1, 5):
        val = ws.cell(row=row, column=col).value
        if val:
            print(f"  Row {row}, Col {col}: {val}")

# Show date row
print("\nDate row (Row 6) - First 10 columns:")
for col in range(5, 15):
    cell = ws.cell(row=6, column=col)
    print(f"  Col {col}: {cell.value} ({type(cell.value).__name__})")

# Show vendor rows and formulas
print("\nVendor rows with SUMPRODUCT formulas:")
vendor_found = 0
for row in range(9, 50):
    vendor = ws.cell(row=row, column=2).value
    if vendor and not str(vendor).startswith(('VENDOR', 'HUMAN', 'GOVERN', 'STRAT', 'LOAN', 'OPER')):
        formula_cell = ws.cell(row=row, column=5)
        formula = str(formula_cell.value) if formula_cell.value else "EMPTY"
        if 'SUMPRODUCT' in formula:
            print(f"  Row {row}: Vendor={vendor}")
            print(f"         Formula: {formula[:100]}...")
            vendor_found += 1
            if vendor_found >= 3:
                break

# ============================================================================
# DIAGNOSTIC 7: Identify specific issues
# ============================================================================
print("\n" + "=" * 80)
print("DIAGNOSTIC 7: IDENTIFIED ISSUES AND RECOMMENDATIONS")
print("=" * 80)

issues = []

# Check 1: Calendar start date vs source dates
ws = wb['Treasury_Calendar']
cal_start = ws.cell(row=6, column=4).value
if isinstance(cal_start, datetime):
    print(f"\n1. Calendar Start Date: {cal_start.date()}")

    # Check if source data has entries before calendar
    ws_src = wb['SRC_Collections']
    for row in range(4, 20):
        src_date = ws_src.cell(row=row, column=8).value
        if isinstance(src_date, datetime) and src_date.date() >= cal_start.date():
            print(f"   ✓ Found matching source date: {src_date.date()}")
            break
    else:
        issues.append("No source dates match calendar range")

# Check 2: Formula column reference accuracy
print("\n2. Formula Column References:")
ws = wb['Treasury_Calendar']

# Find a SUMIF formula and parse it
for row in range(8, 30):
    cell = ws.cell(row=row, column=4)
    if cell.value and 'SUMIF' in str(cell.value):
        formula = str(cell.value)
        # Extract source sheet name
        import re
        match = re.search(r'SRC_\w+', formula)
        if match:
            src_name = match.group()
            print(f"   Checking {src_name} formula...")

            # Get column letters from formula
            date_match = re.search(r'\.\$([A-Z])\$\d+:\$([A-Z])\$', formula)
            amount_match = re.search(r',([A-Z])\$\d+\)', formula)

            if date_match:
                date_col_letter = date_match.group(1)
                print(f"   Formula uses column {date_col_letter} for date criteria")

            # Check against actual source sheet structure
            ws_src = wb[src_name]
            header_row = 3
            for col in range(1, 12):
                header = ws_src.cell(row=header_row, column=col).value
                if header and 'Date' in str(header):
                    from openpyxl.utils import get_column_letter
                    actual_date_col = get_column_letter(col)
                    print(f"   Actual date column in source: {actual_date_col} ({header})")
                    if actual_date_col != date_col_letter:
                        issues.append(f"{src_name}: Formula uses {date_col_letter} but date is in {actual_date_col}")
                    break
        break

# Check 3: Amount column contains formulas vs values
print("\n3. Source Sheet Amount Column Content:")
for sheet_name in ['SRC_Collections', 'SRC_OPeX']:
    ws = wb[sheet_name]
    amt_cell = ws.cell(row=4, column=7)  # Column G
    print(f"   {sheet_name} Col G Row 4: {str(amt_cell.value)[:60]}")
    if amt_cell.value and '=' in str(amt_cell.value):
        print(f"   → Contains FORMULA (will calculate in Excel/LibreOffice)")

# Summary
print("\n" + "=" * 80)
print("SUMMARY OF ISSUES")
print("=" * 80)

if issues:
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
else:
    print("  No critical issues found in formula structure.")
    print("\n  NOTE: Formulas are text in openpyxl - they will calculate when opened in Excel/LibreOffice.")
    print("  The Amount(SAR) columns contain VLOOKUP formulas that need to be calculated first.")
    print("  SUMIF formulas then aggregate these calculated values.")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
