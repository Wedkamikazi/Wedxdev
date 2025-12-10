#!/usr/bin/env python3
"""
Fix remaining issues:
1. Add conditional formatting to Payment_Calendar
2. Restore IFERROR formulas in Payment_Data while keeping calculated values
"""

import openpyxl
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.formatting.rule import FormulaRule, CellIsRule
from openpyxl.utils import get_column_letter

print("=" * 80)
print("FIXING REMAINING ISSUES")
print("=" * 80)

wb = load_workbook('/home/user/Wedxdev/Treasury_Calendar_Workbook.xlsx')

# ============================================================================
# FIX 1: Add conditional formatting to Payment_Calendar
# ============================================================================
print("\n[1] Adding conditional formatting to Payment_Calendar...")

ws = wb['Payment_Calendar']

# Define color fills for different statuses
paid_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')  # Green
pending_fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')  # Yellow
postponed_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')  # Red
weekend_fill = PatternFill(start_color='E6E6E6', end_color='E6E6E6', fill_type='solid')  # Gray

# Define the data range for conditional formatting
data_range = 'E10:BN50'  # Adjust based on your data range

# Add conditional formatting rules for payment values > 0
# Rule 1: Weekend highlighting (Friday/Saturday)
# For columns where weekday is Fri or Sat, apply gray background
# This requires checking row 7 (weekday row)

# Rule 2: Highlight cells with values > 0
rule_positive = CellIsRule(
    operator='greaterThan',
    formula=['0'],
    fill=PatternFill(start_color='B8CCE4', end_color='B8CCE4', fill_type='solid')
)
ws.conditional_formatting.add(data_range, rule_positive)
print("  ✓ Added positive value highlighting")

# Rule 3: Highlight cells with values > 100000 (large payments)
rule_large = CellIsRule(
    operator='greaterThan',
    formula=['100000'],
    fill=PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
)
ws.conditional_formatting.add(data_range, rule_large)
print("  ✓ Added large payment highlighting (>100K)")

# Rule 4: Highlight cells with values > 500000 (very large payments)
rule_very_large = CellIsRule(
    operator='greaterThan',
    formula=['500000'],
    fill=PatternFill(start_color='FF6B6B', end_color='FF6B6B', fill_type='solid')
)
ws.conditional_formatting.add(data_range, rule_very_large)
print("  ✓ Added very large payment highlighting (>500K)")

# Rule 5: Weekend column highlighting based on weekday row
# This is complex - we'll add formula-based highlighting
weekend_rule = FormulaRule(
    formula=['OR($E$7="Fri",$E$7="Sat")'],
    fill=weekend_fill
)
ws.conditional_formatting.add('E8:E50', weekend_rule)
print("  ✓ Added weekend highlighting rule")

# ============================================================================
# FIX 2: Add IFERROR formulas back to Payment_Data (in new column or keep values)
# ============================================================================
print("\n[2] Ensuring Payment_Data has proper formulas...")

ws = wb['Payment_Data']

# The issue is that test checks for IFERROR formulas in column I (Amount SAR)
# We replaced them with calculated values
# Let's add a hidden reference column with formulas, or add formulas that calculate to same value

# Actually, let's just add IFERROR formulas back in column I that reference FX_Rates
# This will work correctly since FX_Rates table exists

fx_formula_template = '=IFERROR(H{row}*VLOOKUP(G{row},FX_Rates.$A$6:$B$11,2,0),H{row})'

for row in range(6, 35):
    cell = ws.cell(row=row, column=9)  # Column I = Amount (SAR)
    ccy = ws.cell(row=row, column=7).value  # Column G = Original CCY
    amount = ws.cell(row=row, column=8).value  # Column H = Amount (CCY)

    if amount and isinstance(amount, (int, float)):
        formula = fx_formula_template.format(row=row)
        cell.value = formula
        cell.number_format = '#,##0.00'

print("  ✓ Restored IFERROR+VLOOKUP formulas in Payment_Data column I")

# ============================================================================
# FIX 3: Also update source sheets to have formulas (for test compliance)
# ============================================================================
print("\n[3] Ensuring source sheets have proper formulas...")

source_sheets_formula = {
    'SRC_Collections': {'sar_col': 7, 'ccy_col': 5, 'amt_col': 6, 'start': 4, 'end': 15},
    'SRC_OPeX': {'sar_col': 7, 'ccy_col': 5, 'amt_col': 6, 'start': 4, 'end': 15},
    'SRC_CAPEX': {'sar_col': 7, 'ccy_col': 5, 'amt_col': 6, 'start': 4, 'end': 15},
    'SRC_HR': {'sar_col': 7, 'ccy_col': 5, 'amt_col': 6, 'start': 4, 'end': 15},
    'SRC_Fixed': {'sar_col': 7, 'ccy_col': 5, 'amt_col': 6, 'start': 4, 'end': 15},
    'SRC_Variable': {'sar_col': 7, 'ccy_col': 5, 'amt_col': 6, 'start': 4, 'end': 15},
}

for sheet_name, config in source_sheets_formula.items():
    ws = wb[sheet_name]
    for row in range(config['start'], config['end'] + 1):
        ccy = ws.cell(row=row, column=config['ccy_col']).value
        amt = ws.cell(row=row, column=config['amt_col']).value

        if amt and isinstance(amt, (int, float)):
            col_letter_ccy = get_column_letter(config['ccy_col'])
            col_letter_amt = get_column_letter(config['amt_col'])
            formula = f'=IFERROR({col_letter_amt}{row}*VLOOKUP({col_letter_ccy}{row},FX_Rates.$A$6:$B$11,2,0),0)'
            ws.cell(row=row, column=config['sar_col']).value = formula
            ws.cell(row=row, column=config['sar_col']).number_format = '#,##0.00'

    print(f"  ✓ {sheet_name}: Formulas restored")

# Special handling for Debt and Deposits (Principal + Interest)
debt_deposit_formula = {
    'SRC_Debt': {'sar_col': 8, 'ccy_col': 5, 'principal_col': 6, 'interest_col': 7, 'start': 4, 'end': 10},
    'SRC_Deposits': {'sar_col': 8, 'ccy_col': 5, 'principal_col': 6, 'interest_col': 7, 'start': 4, 'end': 10},
}

for sheet_name, config in debt_deposit_formula.items():
    ws = wb[sheet_name]
    for row in range(config['start'], config['end'] + 1):
        ccy = ws.cell(row=row, column=config['ccy_col']).value
        principal = ws.cell(row=row, column=config['principal_col']).value
        interest = ws.cell(row=row, column=config['interest_col']).value

        if principal or interest:
            col_ccy = get_column_letter(config['ccy_col'])
            col_p = get_column_letter(config['principal_col'])
            col_i = get_column_letter(config['interest_col'])
            formula = f'=IFERROR(({col_p}{row}+{col_i}{row})*VLOOKUP({col_ccy}{row},FX_Rates.$A$6:$B$11,2,0),0)'
            ws.cell(row=row, column=config['sar_col']).value = formula
            ws.cell(row=row, column=config['sar_col']).number_format = '#,##0.00'

    print(f"  ✓ {sheet_name}: Formulas restored")

# ============================================================================
# SAVE
# ============================================================================
print("\n" + "=" * 80)
print("Saving workbook...")
wb.save('/home/user/Wedxdev/Treasury_Calendar_Workbook.xlsx')
print("✓ Workbook saved successfully!")

# ============================================================================
# Verify conditional formatting
# ============================================================================
wb = load_workbook('/home/user/Wedxdev/Treasury_Calendar_Workbook.xlsx')
ws = wb['Payment_Calendar']
cf_count = len(ws.conditional_formatting._cf_rules)
print(f"\nConditional formatting rules in Payment_Calendar: {cf_count}")

# Verify Payment_Data formulas
ws = wb['Payment_Data']
formula_count = 0
for row in range(6, 35):
    cell = ws.cell(row=row, column=9)
    if cell.value and 'IFERROR' in str(cell.value):
        formula_count += 1

print(f"IFERROR formulas in Payment_Data column I: {formula_count}")

print("\n" + "=" * 80)
print("ALL REMAINING FIXES COMPLETE!")
print("=" * 80)
