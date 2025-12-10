#!/usr/bin/env python3
"""
Fix script to regenerate Treasury Calendar Workbook with proper date handling
and all missing headers/formulas
"""

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation
from datetime import datetime, timedelta

def parse_date(date_str):
    """Convert date string to datetime object"""
    if isinstance(date_str, datetime):
        return date_str
    if isinstance(date_str, str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return date_str
    return date_str

# Load existing workbook
print("Loading existing workbook...")
wb = openpyxl.load_workbook('/home/user/Wedxdev/Treasury_Calendar_Workbook.xlsx')

# ============================================================================
# FIX 1: Convert all date strings to actual dates in source sheets
# ============================================================================
print("\nFIX 1: Converting date strings to datetime objects...")

source_sheets_date_cols = {
    'SRC_Collections': [8],      # Column H = Expected Date
    'SRC_OPeX': [8],             # Column H = Due Date
    'SRC_CAPEX': [8],            # Column H = Payment Date
    'SRC_HR': [8],               # Column H = Payment Date
    'SRC_Debt': [9, 12],         # Column I = Payment Date, L = Maturity Date
    'SRC_Fixed': [8, 10],        # Column H = Due Date, J = Contract End
    'SRC_Variable': [8],         # Column H = Due Date
    'SRC_Deposits': [9],         # Column I = Maturity Date
}

for sheet_name, date_cols in source_sheets_date_cols.items():
    ws = wb[sheet_name]
    print(f"  Processing {sheet_name}...")
    for row in range(4, 100):
        for col in date_cols:
            cell = ws.cell(row=row, column=col)
            if cell.value and isinstance(cell.value, str):
                # Check if it looks like a date
                if '-' in str(cell.value) and len(str(cell.value)) >= 8:
                    try:
                        cell.value = parse_date(cell.value)
                        cell.number_format = 'YYYY-MM-DD'
                    except:
                        pass

# ============================================================================
# FIX 2: Fix Payment_Data dates
# ============================================================================
print("\nFIX 2: Fixing Payment_Data dates...")

ws = wb['Payment_Data']
date_columns = [10, 11, 13]  # J=Due Date, K=Maturity Date, M=Payment Date

for row in range(6, 200):
    for col in date_columns:
        cell = ws.cell(row=row, column=col)
        if cell.value and isinstance(cell.value, str):
            if '-' in str(cell.value) and len(str(cell.value)) >= 8:
                try:
                    cell.value = parse_date(cell.value)
                    cell.number_format = 'YYYY-MM-DD'
                except:
                    pass

# ============================================================================
# FIX 3: Add DATE row to Payment Calendar (Row 6 needs actual dates)
# ============================================================================
print("\nFIX 3: Adding DATE row to Payment Calendar...")

ws = wb['Payment_Calendar']
start_date = datetime(2024, 12, 1)
num_days = 60
header_col_start = 5

# Define styles
header_fill = PatternFill(start_color='2E5090', end_color='2E5090', fill_type='solid')
alt_fill = PatternFill(start_color='F5F7FA', end_color='F5F7FA', fill_type='solid')
thin_border = Border(
    left=Side(style='thin', color='D1D9E6'),
    right=Side(style='thin', color='D1D9E6'),
    top=Side(style='thin', color='D1D9E6'),
    bottom=Side(style='thin', color='D1D9E6')
)

# Insert a new row for DATE between Day and Weekday
# Current structure: Row 3=Year, Row 4=Month, Row 5=Week#, Row 6=Day, Row 7=Weekday
# Need: Row 3=Year, Row 4=Month, Row 5=Week#, Row 6=DATE, Row 7=Day, Row 8=Weekday

# Actually, let's just update the formulas to reference the correct date row
# The Treasury_Calendar has dates in Row 6, Payment_Calendar has day numbers in Row 6
# We need to either add a date row or change the formula to calculate the date

# Simplest fix: Add actual dates to Row 6 in Payment Calendar
# But first check what's there
print("  Current Row 6 values (first 10 cols):")
for col in range(5, 15):
    print(f"    Col {col}: {ws.cell(row=6, column=col).value}")

# The issue is that Payment Calendar Row 6 has day numbers, not full dates
# Let's add actual dates to a hidden helper row or fix the formulas

# Add DATE values to row 6 (replacing day numbers with actual dates)
for day_offset in range(num_days):
    current_date = start_date + timedelta(days=day_offset)
    col = header_col_start + day_offset

    # Store the date in row 6
    cell = ws.cell(row=6, column=col)
    cell.value = current_date
    cell.number_format = 'D'  # Just show day number for display
    cell.font = Font(name='Calibri', size=10, bold=True)
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.border = thin_border

print("  Added actual dates to Row 6 (displayed as day numbers)")

# ============================================================================
# FIX 4: Update SUMPRODUCT formulas in Payment Calendar to use proper date ref
# ============================================================================
print("\nFIX 4: Updating Payment Calendar formulas...")

# The formulas should now work because Row 6 contains actual dates
# SUMPRODUCT compares Payment_Data.$J$6:$J$100 (dates) with E$6 (now a date)

# Verify formula structure
vendor_rows = range(10, 45)  # Approximate vendor row range
for row in vendor_rows:
    for col in range(header_col_start, header_col_start + 5):
        cell = ws.cell(row=row, column=col)
        if cell.value and isinstance(cell.value, str) and 'SUMPRODUCT' in str(cell.value):
            # Formula looks like: =IFERROR(SUMPRODUCT((Payment_Data.$B$6:$B$100="VND-001")*(Payment_Data.$J$6:$J$100=E$6)*(Payment_Data.$I$6:$I$100)),0)
            # This should now work correctly
            print(f"  Row {row} Col {col}: Formula intact")
            break
    else:
        continue
    break

# ============================================================================
# FIX 5: Add missing column headers to Payment Calendar rows 4-7
# ============================================================================
print("\nFIX 5: Adding header labels to Payment Calendar...")

# Row 3 headers (already exists: Category, Vendor/Payee, CCY, Status)
# Rows 4-7 columns A-D should be merged or labeled

header_labels = {
    4: 'Month',
    5: 'Week',
    6: 'Date',
    7: 'Day'
}

for row, label in header_labels.items():
    # Set label in column A
    cell = ws.cell(row=row, column=1)
    cell.value = label
    cell.font = Font(name='Calibri', size=10, bold=True, color='FFFFFF')
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal='center', vertical='center')
    cell.border = thin_border

    # Fill columns B-D with header style
    for col in range(2, 5):
        cell = ws.cell(row=row, column=col)
        cell.fill = header_fill
        cell.border = thin_border

print("  Added row labels to Payment Calendar")

# ============================================================================
# SAVE THE FIXED WORKBOOK
# ============================================================================
print("\nSaving fixed workbook...")
wb.save('/home/user/Wedxdev/Treasury_Calendar_Workbook.xlsx')
print("✓ Workbook saved successfully!")

# ============================================================================
# VERIFY THE FIXES
# ============================================================================
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

# Reload and verify
wb = openpyxl.load_workbook('/home/user/Wedxdev/Treasury_Calendar_Workbook.xlsx')

# Check Payment_Data dates
ws = wb['Payment_Data']
print("\nPayment_Data date column (J) - first 5 rows:")
for row in range(6, 11):
    cell = ws.cell(row=row, column=10)
    print(f"  Row {row}: {cell.value} (type: {type(cell.value).__name__})")

# Check SRC_Collections dates
ws = wb['SRC_Collections']
print("\nSRC_Collections date column (H) - first 5 rows:")
for row in range(4, 9):
    cell = ws.cell(row=row, column=8)
    print(f"  Row {row}: {cell.value} (type: {type(cell.value).__name__})")

# Check Payment Calendar Row 6
ws = wb['Payment_Calendar']
print("\nPayment_Calendar Row 6 (DATE row) - first 5 date columns:")
for col in range(5, 10):
    cell = ws.cell(row=6, column=col)
    print(f"  Col {col}: {cell.value} (type: {type(cell.value).__name__})")

# Check header labels
print("\nPayment_Calendar header labels (Column A):")
for row in range(3, 8):
    cell = ws.cell(row=row, column=1)
    print(f"  Row {row}: {cell.value}")

print("\n" + "=" * 70)
print("FIXES COMPLETE!")
print("=" * 70)
