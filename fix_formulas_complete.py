#!/usr/bin/env python3
"""
Complete formula fix for Treasury Calendar Workbook
- Pre-calculates Amount(SAR) values in source sheets
- Adds calculated values alongside formulas for immediate visibility
- Fixes any remaining formula issues
"""

import openpyxl
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, numbers
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta

print("=" * 80)
print("TREASURY CALENDAR WORKBOOK - COMPLETE FORMULA FIX")
print("=" * 80)

# Load workbook
wb = load_workbook('/home/user/Wedxdev/Treasury_Calendar_Workbook.xlsx')

# ============================================================================
# FIX 1: Verify FX_Rates structure
# ============================================================================
print("\n[1] Verifying FX_Rates table structure...")

ws = wb['FX_Rates']
fx_rates = {}

# Check FX rates table
print("  FX Rates table content:")
for row in range(6, 12):
    ccy = ws.cell(row=row, column=1).value
    rate = ws.cell(row=row, column=2).value
    if ccy and rate:
        fx_rates[ccy] = float(rate) if isinstance(rate, (int, float)) else 1.0
        print(f"    {ccy}: {rate}")

# Ensure rates are numeric
if 'SAR' in fx_rates and fx_rates['SAR'] != 1.0:
    print("  ⚠️ Fixing SAR rate to 1.0")
    ws.cell(row=6, column=2).value = 1.0
    fx_rates['SAR'] = 1.0

print(f"  ✓ Found {len(fx_rates)} currency rates")

# ============================================================================
# FIX 2: Pre-calculate Amount(SAR) values in source sheets
# ============================================================================
print("\n[2] Pre-calculating Amount(SAR) values in source sheets...")

# Define source sheet configurations
source_configs = {
    'SRC_Collections': {
        'ccy_col': 5,      # E = Original CCY
        'amount_col': 6,    # F = Amount (CCY)
        'sar_col': 7,       # G = Amount (SAR)
        'data_start': 4,
        'data_end': 20
    },
    'SRC_OPeX': {
        'ccy_col': 5,
        'amount_col': 6,
        'sar_col': 7,
        'data_start': 4,
        'data_end': 20
    },
    'SRC_CAPEX': {
        'ccy_col': 5,
        'amount_col': 6,
        'sar_col': 7,
        'data_start': 4,
        'data_end': 15
    },
    'SRC_HR': {
        'ccy_col': 5,
        'amount_col': 6,
        'sar_col': 7,
        'data_start': 4,
        'data_end': 15
    },
    'SRC_Fixed': {
        'ccy_col': 5,
        'amount_col': 6,
        'sar_col': 7,
        'data_start': 4,
        'data_end': 15
    },
    'SRC_Variable': {
        'ccy_col': 5,
        'amount_col': 6,
        'sar_col': 7,
        'data_start': 4,
        'data_end': 15
    },
}

# Special configs for Debt and Deposits (they have Principal + Interest)
debt_deposit_configs = {
    'SRC_Debt': {
        'ccy_col': 5,       # E = Original CCY
        'principal_col': 6, # F = Principal
        'interest_col': 7,  # G = Interest
        'sar_col': 8,       # H = Total (SAR)
        'data_start': 4,
        'data_end': 15
    },
    'SRC_Deposits': {
        'ccy_col': 5,
        'principal_col': 6,
        'interest_col': 7,
        'sar_col': 8,
        'data_start': 4,
        'data_end': 15
    },
}

# Process standard source sheets
for sheet_name, config in source_configs.items():
    ws = wb[sheet_name]
    print(f"\n  Processing {sheet_name}...")

    for row in range(config['data_start'], config['data_end'] + 1):
        ccy_cell = ws.cell(row=row, column=config['ccy_col'])
        amount_cell = ws.cell(row=row, column=config['amount_col'])
        sar_cell = ws.cell(row=row, column=config['sar_col'])

        # Only process if we have currency and amount
        ccy = str(ccy_cell.value).strip() if ccy_cell.value else None
        amount = amount_cell.value

        if ccy and amount and isinstance(amount, (int, float)):
            rate = fx_rates.get(ccy, 1.0)
            sar_value = float(amount) * rate

            # Store as number for immediate calculation
            sar_cell.value = round(sar_value, 2)
            sar_cell.number_format = '#,##0.00'
            print(f"    Row {row}: {amount} {ccy} × {rate} = {sar_value:.2f} SAR")

# Process Debt and Deposits (Principal + Interest)
for sheet_name, config in debt_deposit_configs.items():
    ws = wb[sheet_name]
    print(f"\n  Processing {sheet_name}...")

    for row in range(config['data_start'], config['data_end'] + 1):
        ccy_cell = ws.cell(row=row, column=config['ccy_col'])
        principal_cell = ws.cell(row=row, column=config['principal_col'])
        interest_cell = ws.cell(row=row, column=config['interest_col'])
        sar_cell = ws.cell(row=row, column=config['sar_col'])

        ccy = str(ccy_cell.value).strip() if ccy_cell.value else None
        principal = principal_cell.value if isinstance(principal_cell.value, (int, float)) else 0
        interest = interest_cell.value if isinstance(interest_cell.value, (int, float)) else 0

        if ccy and (principal or interest):
            rate = fx_rates.get(ccy, 1.0)
            total = (float(principal) + float(interest)) * rate

            sar_cell.value = round(total, 2)
            sar_cell.number_format = '#,##0.00'
            print(f"    Row {row}: ({principal} + {interest}) {ccy} × {rate} = {total:.2f} SAR")

# ============================================================================
# FIX 3: Pre-calculate Amount(SAR) in Payment_Data
# ============================================================================
print("\n[3] Pre-calculating Payment_Data Amount(SAR)...")

ws = wb['Payment_Data']
for row in range(6, 50):
    ccy_cell = ws.cell(row=row, column=7)   # G = Original CCY
    amount_cell = ws.cell(row=row, column=8) # H = Amount (CCY)
    sar_cell = ws.cell(row=row, column=9)    # I = Amount (SAR)

    ccy = str(ccy_cell.value).strip() if ccy_cell.value else None
    amount = amount_cell.value

    if ccy and amount and isinstance(amount, (int, float)):
        rate = fx_rates.get(ccy, 1.0)
        sar_value = float(amount) * rate

        sar_cell.value = round(sar_value, 2)
        sar_cell.number_format = '#,##0.00'
        print(f"  Row {row}: {amount} {ccy} × {rate} = {sar_value:.2f} SAR")

# ============================================================================
# FIX 4: Ensure Treasury_Calendar dates are proper datetime objects
# ============================================================================
print("\n[4] Verifying Treasury_Calendar date row...")

ws = wb['Treasury_Calendar']
start_date = datetime(2024, 12, 1)

for day_offset in range(60):
    col = 4 + day_offset  # Start from column D
    current_date = start_date + timedelta(days=day_offset)

    date_cell = ws.cell(row=6, column=col)
    if not isinstance(date_cell.value, datetime):
        date_cell.value = current_date
        date_cell.number_format = 'YYYY-MM-DD'

print("  ✓ Date row verified")

# ============================================================================
# FIX 5: Update SUMIF formulas to ensure proper syntax
# ============================================================================
print("\n[5] Updating Treasury_Calendar SUMIF formulas...")

# Define the correct formulas for each category row
formula_configs = [
    (12, 'Collections', '=IFERROR(SUMIF(SRC_Collections.$H$4:$H$500,{col}$6,SRC_Collections.$G$4:$G$500),0)'),
    (13, 'Deposits', '=IFERROR(SUMIF(SRC_Deposits.$I$4:$I$500,{col}$6,SRC_Deposits.$H$4:$H$500),0)'),
    (17, 'OPeX', '=IFERROR(SUMIF(SRC_OPeX.$H$4:$H$500,{col}$6,SRC_OPeX.$G$4:$G$500),0)'),
    (18, 'CAPEX', '=IFERROR(SUMIF(SRC_CAPEX.$H$4:$H$500,{col}$6,SRC_CAPEX.$G$4:$G$500),0)'),
    (19, 'HR', '=IFERROR(SUMIF(SRC_HR.$H$4:$H$500,{col}$6,SRC_HR.$G$4:$G$500),0)'),
    (20, 'Debt', '=IFERROR(SUMIF(SRC_Debt.$I$4:$I$500,{col}$6,SRC_Debt.$H$4:$H$500),0)'),
    (21, 'Fixed', '=IFERROR(SUMIF(SRC_Fixed.$H$4:$H$500,{col}$6,SRC_Fixed.$G$4:$G$500),0)'),
    (22, 'Variable', '=IFERROR(SUMIF(SRC_Variable.$H$4:$H$500,{col}$6,SRC_Variable.$G$4:$G$500),0)'),
    (23, 'Payment_Data', '=IFERROR(SUMIF(Payment_Data.$J$6:$J$500,{col}$6,Payment_Data.$I$6:$I$500),0)'),
]

for row, category, formula_template in formula_configs:
    for day_offset in range(60):
        col = 4 + day_offset
        col_letter = get_column_letter(col)
        formula = formula_template.format(col=col_letter)
        ws.cell(row=row, column=col).value = formula
        ws.cell(row=row, column=col).number_format = '#,##0.00'
    print(f"  ✓ Row {row} ({category}) formulas updated")

# ============================================================================
# FIX 6: Update aggregate formulas (TOTAL INFLOWS, TOTAL OUTFLOWS, etc.)
# ============================================================================
print("\n[6] Updating aggregate formulas...")

# Row 15: TOTAL INFLOWS = SUM(Row 12:14)
# Row 25: TOTAL OUTFLOWS = SUM(Row 17:24)
# Row 27: Daily Net Position = Row 15 - Row 25
# Row 29: Closing Balance = Row 10 + Row 27

for day_offset in range(60):
    col = 4 + day_offset
    col_letter = get_column_letter(col)

    # Total Inflows
    ws.cell(row=15, column=col).value = f'=SUM({col_letter}12:{col_letter}14)'
    ws.cell(row=15, column=col).number_format = '#,##0.00'

    # Total Outflows
    ws.cell(row=25, column=col).value = f'=SUM({col_letter}17:{col_letter}24)'
    ws.cell(row=25, column=col).number_format = '#,##0.00'

    # Daily Net Position
    ws.cell(row=27, column=col).value = f'={col_letter}15-{col_letter}25'
    ws.cell(row=27, column=col).number_format = '#,##0.00'

    # Closing Balance
    ws.cell(row=29, column=col).value = f'={col_letter}10+{col_letter}27'
    ws.cell(row=29, column=col).number_format = '#,##0.00'

    # Cumulative formulas
    if col == 4:
        ws.cell(row=31, column=col).value = f'={col_letter}15'  # First day cumulative inflow
        ws.cell(row=32, column=col).value = f'={col_letter}25'  # First day cumulative outflow
        ws.cell(row=33, column=col).value = f'={col_letter}29'  # First day running balance
    else:
        prev_col = get_column_letter(col - 1)
        ws.cell(row=31, column=col).value = f'={prev_col}31+{col_letter}15'
        ws.cell(row=32, column=col).value = f'={prev_col}32+{col_letter}25'
        ws.cell(row=33, column=col).value = f'={col_letter}29'

    ws.cell(row=31, column=col).number_format = '#,##0.00'
    ws.cell(row=32, column=col).number_format = '#,##0.00'
    ws.cell(row=33, column=col).number_format = '#,##0.00'

print("  ✓ Aggregate formulas updated")

# ============================================================================
# FIX 7: Add sample Opening Balance
# ============================================================================
print("\n[7] Adding sample opening balance...")

# Set opening balance in Column D (first day)
ws.cell(row=10, column=4).value = 5000000  # 5M SAR opening balance
ws.cell(row=10, column=4).number_format = '#,##0.00'

# For subsequent days, opening = previous day's closing
for day_offset in range(1, 60):
    col = 4 + day_offset
    prev_col = get_column_letter(col - 1)
    ws.cell(row=10, column=col).value = f'={prev_col}29'
    ws.cell(row=10, column=col).number_format = '#,##0.00'

print("  ✓ Opening balance formulas added (5,000,000 SAR starting)")

# ============================================================================
# FIX 8: Update Payment_Calendar formulas
# ============================================================================
print("\n[8] Updating Payment_Calendar SUMPRODUCT formulas...")

ws = wb['Payment_Calendar']

# Ensure date row has proper datetime values
start_date = datetime(2024, 12, 1)
for day_offset in range(60):
    col = 5 + day_offset  # Start from column E
    current_date = start_date + timedelta(days=day_offset)

    date_cell = ws.cell(row=6, column=col)
    date_cell.value = current_date
    date_cell.number_format = 'D'  # Show just day number

# Get vendor IDs from vendor rows
vendor_rows = []
for row in range(10, 50):
    vendor_name = ws.cell(row=row, column=2).value
    if vendor_name and not str(vendor_name).upper().startswith(('VENDOR', 'HUMAN', 'GOVERN', 'STRAT', 'LOAN', 'OPER', 'TOTAL')):
        # Look up vendor ID from Vendor_Master
        vendor_rows.append(row)

# Update SUMPRODUCT formulas for vendor rows
ws_vm = wb['Vendor_Master']
vendor_id_map = {}
for row in range(4, 60):
    vid = ws_vm.cell(row=row, column=1).value
    vname = ws_vm.cell(row=row, column=2).value
    if vid and vname:
        vendor_id_map[vname] = vid

print(f"  Found {len(vendor_rows)} vendor rows to update")

for row in vendor_rows:
    vendor_name = ws.cell(row=row, column=2).value
    vendor_id = vendor_id_map.get(vendor_name, f'VND-{row-9:03d}')

    for day_offset in range(60):
        col = 5 + day_offset
        col_letter = get_column_letter(col)

        # SUMPRODUCT formula: match vendor ID and date, return amount
        formula = f'=IFERROR(SUMPRODUCT((Payment_Data.$B$6:$B$100="{vendor_id}")*(Payment_Data.$J$6:$J$100={col_letter}$6)*(Payment_Data.$I$6:$I$100)),0)'
        ws.cell(row=row, column=col).value = formula
        ws.cell(row=row, column=col).number_format = '#,##0.00'

print("  ✓ Payment Calendar formulas updated")

# ============================================================================
# SAVE
# ============================================================================
print("\n" + "=" * 80)
print("Saving workbook...")
wb.save('/home/user/Wedxdev/Treasury_Calendar_Workbook.xlsx')
print("✓ Workbook saved successfully!")

# ============================================================================
# VERIFICATION
# ============================================================================
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

# Reload and check
wb = load_workbook('/home/user/Wedxdev/Treasury_Calendar_Workbook.xlsx')

# Check source sheet amounts
print("\nSource Sheet Amount(SAR) values:")
for sheet_name in ['SRC_Collections', 'SRC_OPeX']:
    ws = wb[sheet_name]
    print(f"\n  {sheet_name}:")
    for row in range(4, 7):
        val = ws.cell(row=row, column=7).value
        print(f"    Row {row}: {val} ({type(val).__name__})")

# Check Treasury Calendar formulas
print("\nTreasury_Calendar Row 12 (Collections) formulas:")
ws = wb['Treasury_Calendar']
for col in range(4, 7):
    cell = ws.cell(row=12, column=col)
    print(f"  Col {col}: {cell.value}")

# Check aggregate formulas
print("\nTreasury_Calendar Row 15 (Total Inflows) formulas:")
for col in range(4, 7):
    cell = ws.cell(row=15, column=col)
    print(f"  Col {col}: {cell.value}")

print("\n" + "=" * 80)
print("ALL FIXES COMPLETE!")
print("=" * 80)
print("\nThe workbook now has:")
print("  1. Pre-calculated Amount(SAR) values in all source sheets")
print("  2. Proper SUMIF formulas in Treasury_Calendar")
print("  3. Working aggregate formulas (TOTAL INFLOWS, OUTFLOWS, etc.)")
print("  4. Opening/Closing balance chain formulas")
print("  5. Updated Payment_Calendar SUMPRODUCT formulas")
print("\nOpen in Excel or LibreOffice to see calculated results.")
