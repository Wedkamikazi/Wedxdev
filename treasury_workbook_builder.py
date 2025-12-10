#!/usr/bin/env python3
"""
Treasury Calendar Workbook Builder
Enterprise-grade Treasury Calendar with Payment Calendar integration
Compatible with LibreOffice Calc (no LET, XLOOKUP, or advanced Excel-only functions)
Main Currency: SAR | Secondary: USD, AED, EUR, GBP, SGD
Saudi Calendar: Week starts Sunday, Weekend is Friday & Saturday
"""

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import (
    Font, Fill, PatternFill, Border, Side, Alignment,
    NamedStyle, Protection, GradientFill
)
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import (
    FormulaRule, ColorScaleRule, DataBarRule,
    CellIsRule, Rule
)
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
from datetime import datetime, timedelta
from decimal import Decimal
import calendar

def parse_date(date_str):
    """Convert date string to datetime object for proper Excel date handling"""
    if isinstance(date_str, datetime):
        return date_str
    if isinstance(date_str, str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%d-%m-%Y')
            except ValueError:
                return date_str
    return date_str

# ============================================================================
# STYLE DEFINITIONS - Professional Treasury Theme
# ============================================================================

class TreasuryStyles:
    """Professional color palette and styling for Treasury workbook"""

    # Color Palette - Modern Professional Theme
    COLORS = {
        # Primary Colors
        'primary_dark': '1B365D',      # Deep Navy
        'primary_medium': '2E5090',    # Royal Blue
        'primary_light': '4A7CC2',     # Soft Blue

        # Accent Colors
        'accent_gold': 'C9A227',        # Treasury Gold
        'accent_green': '2E7D32',       # Success Green
        'accent_red': 'C62828',         # Alert Red
        'accent_orange': 'EF6C00',      # Warning Orange

        # Neutral Colors
        'bg_white': 'FFFFFF',
        'bg_light': 'F5F7FA',
        'bg_alt': 'E8ECF1',
        'border_light': 'D1D9E6',
        'border_medium': 'A0AEC0',
        'text_dark': '2D3748',
        'text_medium': '4A5568',
        'text_light': '718096',

        # Status Colors
        'status_paid': '4CAF50',        # Green
        'status_pending': 'FF9800',     # Orange
        'status_postponed': '9E9E9E',   # Gray
        'status_overdue': 'F44336',     # Red

        # Currency Colors
        'ccy_sar': '1B365D',
        'ccy_usd': '2E7D32',
        'ccy_aed': 'C9A227',
        'ccy_eur': '1565C0',
        'ccy_gbp': '6A1B9A',
        'ccy_sgd': 'C62828',

        # Weekend highlighting (Saudi)
        'weekend_friday': 'FFF3E0',
        'weekend_saturday': 'FFF8E1',
    }

    # Font Definitions
    FONTS = {
        'title': Font(name='Calibri', size=18, bold=True, color='FFFFFF'),
        'header_main': Font(name='Calibri', size=12, bold=True, color='FFFFFF'),
        'header_sub': Font(name='Calibri', size=11, bold=True, color='1B365D'),
        'category': Font(name='Calibri', size=11, bold=True, color='2D3748'),
        'subcategory': Font(name='Calibri', size=10, bold=False, color='4A5568'),
        'data': Font(name='Calibri', size=10, color='2D3748'),
        'data_bold': Font(name='Calibri', size=10, bold=True, color='2D3748'),
        'total': Font(name='Calibri', size=11, bold=True, color='1B365D'),
        'currency': Font(name='Calibri', size=10, color='2D3748'),
        'link': Font(name='Calibri', size=10, color='1565C0', underline='single'),
        'small': Font(name='Calibri', size=9, color='718096'),
    }

    # Fill Patterns
    FILLS = {
        'header_primary': PatternFill(start_color='1B365D', end_color='1B365D', fill_type='solid'),
        'header_secondary': PatternFill(start_color='2E5090', end_color='2E5090', fill_type='solid'),
        'header_tertiary': PatternFill(start_color='4A7CC2', end_color='4A7CC2', fill_type='solid'),
        'row_alt': PatternFill(start_color='F5F7FA', end_color='F5F7FA', fill_type='solid'),
        'row_white': PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid'),
        'total_row': PatternFill(start_color='E8ECF1', end_color='E8ECF1', fill_type='solid'),
        'input_cell': PatternFill(start_color='FFFDE7', end_color='FFFDE7', fill_type='solid'),
        'weekend_fri': PatternFill(start_color='FFF3E0', end_color='FFF3E0', fill_type='solid'),
        'weekend_sat': PatternFill(start_color='FFF8E1', end_color='FFF8E1', fill_type='solid'),
        'status_paid': PatternFill(start_color='C8E6C9', end_color='C8E6C9', fill_type='solid'),
        'status_pending': PatternFill(start_color='FFE0B2', end_color='FFE0B2', fill_type='solid'),
        'status_postponed': PatternFill(start_color='E0E0E0', end_color='E0E0E0', fill_type='solid'),
        'status_overdue': PatternFill(start_color='FFCDD2', end_color='FFCDD2', fill_type='solid'),
        'gold_accent': PatternFill(start_color='FFF8E1', end_color='FFF8E1', fill_type='solid'),
    }

    # Border Styles
    BORDERS = {
        'thin': Border(
            left=Side(style='thin', color='D1D9E6'),
            right=Side(style='thin', color='D1D9E6'),
            top=Side(style='thin', color='D1D9E6'),
            bottom=Side(style='thin', color='D1D9E6')
        ),
        'medium': Border(
            left=Side(style='medium', color='A0AEC0'),
            right=Side(style='medium', color='A0AEC0'),
            top=Side(style='medium', color='A0AEC0'),
            bottom=Side(style='medium', color='A0AEC0')
        ),
        'header': Border(
            left=Side(style='thin', color='1B365D'),
            right=Side(style='thin', color='1B365D'),
            top=Side(style='thin', color='1B365D'),
            bottom=Side(style='medium', color='1B365D')
        ),
        'bottom_thick': Border(
            bottom=Side(style='medium', color='1B365D')
        ),
        'right_thick': Border(
            right=Side(style='medium', color='A0AEC0')
        ),
    }

    # Alignment
    ALIGNMENTS = {
        'center': Alignment(horizontal='center', vertical='center', wrap_text=True),
        'left': Alignment(horizontal='left', vertical='center', wrap_text=True),
        'right': Alignment(horizontal='right', vertical='center'),
        'center_top': Alignment(horizontal='center', vertical='top', wrap_text=True),
        'number': Alignment(horizontal='right', vertical='center'),
    }

    # Number Formats
    NUMBER_FORMATS = {
        'currency_sar': '#,##0.00 "SAR"',
        'currency_usd': '[$$-409]#,##0.00',
        'currency_aed': '#,##0.00 "AED"',
        'currency_eur': '€#,##0.00',
        'currency_gbp': '£#,##0.00',
        'currency_sgd': '#,##0.00 "SGD"',
        'number': '#,##0.00',
        'integer': '#,##0',
        'percentage': '0.00%',
        'date': 'YYYY-MM-DD',
        'date_short': 'DD-MMM',
        'datetime': 'YYYY-MM-DD HH:MM',
    }


class TreasuryWorkbookBuilder:
    """Main builder class for Treasury Calendar workbook"""

    def __init__(self):
        self.wb = Workbook()
        self.styles = TreasuryStyles()
        self.sheets = {}

        # Configuration parameters
        self.config = {
            'base_currency': 'SAR',
            'currencies': ['SAR', 'USD', 'AED', 'EUR', 'GBP', 'SGD'],
            'exchange_rates': {
                'SAR': 1.0000,
                'USD': 3.7500,
                'AED': 1.0210,
                'EUR': 4.1250,
                'GBP': 4.7500,
                'SGD': 2.7800,
            },
            'week_start': 7,  # Sunday = 7 in Saudi Arabia
            'weekend_days': [5, 6],  # Friday=5 (WEEKDAY), Saturday=6
            'fiscal_year_start': 1,  # January
            'calendar_days': 90,  # Default calendar horizon
        }

    def create_all_sheets(self):
        """Create all workbook sheets in proper order"""
        # Remove default sheet
        if 'Sheet' in self.wb.sheetnames:
            del self.wb['Sheet']

        # Create sheets in logical order
        sheet_names = [
            'Config',              # Configuration & Parameters
            'FX_Rates',            # Exchange Rates Table
            'SRC_Collections',     # Source: Collections/Receivables
            'SRC_OPeX',            # Source: Operating Expenditures
            'SRC_CAPEX',           # Source: Capital Expenditures
            'SRC_HR',              # Source: Human Resources/Payroll
            'SRC_Debt',            # Source: Debt Service/Loans
            'SRC_Fixed',           # Source: Fixed Expenses
            'SRC_Variable',        # Source: Variable Expenses
            'SRC_Deposits',        # Source: Deposit Maturities
            'Vendor_Master',       # Vendor/Payee Master List
            'Payment_Data',        # Payment Transaction Data (Single Source of Truth)
            'Treasury_Calendar',   # Main Treasury Calendar View
            'Payment_Calendar',    # Payment Calendar View
        ]

        for name in sheet_names:
            ws = self.wb.create_sheet(title=name)
            self.sheets[name] = ws

        return self

    def build_config_sheet(self):
        """Build Configuration sheet with all parameters"""
        ws = self.sheets['Config']

        # Sheet title
        ws.merge_cells('A1:H1')
        ws['A1'] = 'TREASURY CALENDAR - CONFIGURATION'
        ws['A1'].font = self.styles.FONTS['title']
        ws['A1'].fill = self.styles.FILLS['header_primary']
        ws['A1'].alignment = self.styles.ALIGNMENTS['center']
        ws.row_dimensions[1].height = 35

        # Section 1: General Settings
        row = 3
        ws.merge_cells(f'A{row}:D{row}')
        ws[f'A{row}'] = 'GENERAL SETTINGS'
        ws[f'A{row}'].font = self.styles.FONTS['header_sub']
        ws[f'A{row}'].fill = self.styles.FILLS['total_row']
        ws[f'A{row}'].border = self.styles.BORDERS['bottom_thick']
        row += 1

        settings = [
            ('Base Currency', 'SAR', 'Primary reporting currency'),
            ('Calendar Start Date', datetime.now().strftime('%Y-%m-%d'), 'First date on calendar'),
            ('Calendar Days', '90', 'Number of days to display'),
            ('Fiscal Year Start', '1', 'Month number (1=January)'),
            ('Week Start Day', 'Sunday', 'Saudi calendar standard'),
            ('Weekend Day 1', 'Friday', 'Non-working day'),
            ('Weekend Day 2', 'Saturday', 'Non-working day'),
            ('Organization Name', 'ENTERPRISE TREASURY', 'Company name for reports'),
        ]

        for setting in settings:
            ws[f'A{row}'] = setting[0]
            ws[f'A{row}'].font = self.styles.FONTS['category']
            ws[f'A{row}'].alignment = self.styles.ALIGNMENTS['left']

            ws[f'B{row}'] = setting[1]
            ws[f'B{row}'].font = self.styles.FONTS['data']
            ws[f'B{row}'].fill = self.styles.FILLS['input_cell']
            ws[f'B{row}'].border = self.styles.BORDERS['thin']

            ws[f'C{row}'] = setting[2]
            ws[f'C{row}'].font = self.styles.FONTS['small']
            ws[f'C{row}'].alignment = self.styles.ALIGNMENTS['left']
            row += 1

        # Section 2: Currency Configuration
        row += 2
        ws.merge_cells(f'A{row}:D{row}')
        ws[f'A{row}'] = 'CURRENCY CONFIGURATION'
        ws[f'A{row}'].font = self.styles.FONTS['header_sub']
        ws[f'A{row}'].fill = self.styles.FILLS['total_row']
        ws[f'A{row}'].border = self.styles.BORDERS['bottom_thick']
        row += 1

        # Currency headers
        headers = ['Currency Code', 'Currency Name', 'Rate to SAR', 'Decimal Places']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header
            cell.font = self.styles.FONTS['header_main']
            cell.fill = self.styles.FILLS['header_secondary']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.border = self.styles.BORDERS['header']
        row += 1

        currencies = [
            ('SAR', 'Saudi Riyal', 1.0000, 2),
            ('USD', 'US Dollar', 3.7500, 2),
            ('AED', 'UAE Dirham', 1.0210, 2),
            ('EUR', 'Euro', 4.1250, 2),
            ('GBP', 'British Pound', 4.7500, 2),
            ('SGD', 'Singapore Dollar', 2.7800, 2),
        ]

        for ccy in currencies:
            ws[f'A{row}'] = ccy[0]
            ws[f'A{row}'].font = self.styles.FONTS['data_bold']
            ws[f'A{row}'].alignment = self.styles.ALIGNMENTS['center']
            ws[f'A{row}'].border = self.styles.BORDERS['thin']

            ws[f'B{row}'] = ccy[1]
            ws[f'B{row}'].font = self.styles.FONTS['data']
            ws[f'B{row}'].border = self.styles.BORDERS['thin']

            ws[f'C{row}'] = ccy[2]
            ws[f'C{row}'].font = self.styles.FONTS['data']
            ws[f'C{row}'].number_format = '#,##0.0000'
            ws[f'C{row}'].fill = self.styles.FILLS['input_cell']
            ws[f'C{row}'].border = self.styles.BORDERS['thin']

            ws[f'D{row}'] = ccy[3]
            ws[f'D{row}'].font = self.styles.FONTS['data']
            ws[f'D{row}'].alignment = self.styles.ALIGNMENTS['center']
            ws[f'D{row}'].border = self.styles.BORDERS['thin']
            row += 1

        # Section 3: Payment Status Configuration
        row += 2
        ws.merge_cells(f'A{row}:D{row}')
        ws[f'A{row}'] = 'PAYMENT STATUS CONFIGURATION'
        ws[f'A{row}'].font = self.styles.FONTS['header_sub']
        ws[f'A{row}'].fill = self.styles.FILLS['total_row']
        ws[f'A{row}'].border = self.styles.BORDERS['bottom_thick']
        row += 1

        status_headers = ['Status Code', 'Display Name', 'Color Code', 'Priority']
        for col, header in enumerate(status_headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header
            cell.font = self.styles.FONTS['header_main']
            cell.fill = self.styles.FILLS['header_secondary']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.border = self.styles.BORDERS['header']
        row += 1

        statuses = [
            ('PAID', 'Paid', '4CAF50', 1),
            ('PENDING', 'Pending', 'FF9800', 2),
            ('POSTPONED', 'Postponed', '9E9E9E', 3),
            ('OVERDUE', 'Overdue', 'F44336', 4),
            ('SCHEDULED', 'Scheduled', '2196F3', 5),
            ('CANCELLED', 'Cancelled', '757575', 6),
        ]

        for status in statuses:
            ws[f'A{row}'] = status[0]
            ws[f'A{row}'].font = self.styles.FONTS['data_bold']
            ws[f'A{row}'].alignment = self.styles.ALIGNMENTS['center']
            ws[f'A{row}'].border = self.styles.BORDERS['thin']

            ws[f'B{row}'] = status[1]
            ws[f'B{row}'].font = self.styles.FONTS['data']
            ws[f'B{row}'].border = self.styles.BORDERS['thin']

            ws[f'C{row}'] = status[2]
            ws[f'C{row}'].font = self.styles.FONTS['data']
            ws[f'C{row}'].fill = PatternFill(start_color=status[2], end_color=status[2], fill_type='solid')
            ws[f'C{row}'].border = self.styles.BORDERS['thin']

            ws[f'D{row}'] = status[3]
            ws[f'D{row}'].font = self.styles.FONTS['data']
            ws[f'D{row}'].alignment = self.styles.ALIGNMENTS['center']
            ws[f'D{row}'].border = self.styles.BORDERS['thin']
            row += 1

        # Section 4: Payment Categories
        row += 2
        ws.merge_cells(f'A{row}:D{row}')
        ws[f'A{row}'] = 'PAYMENT CATEGORIES'
        ws[f'A{row}'].font = self.styles.FONTS['header_sub']
        ws[f'A{row}'].fill = self.styles.FILLS['total_row']
        ws[f'A{row}'].border = self.styles.BORDERS['bottom_thick']
        row += 1

        cat_headers = ['Category Code', 'Category Name', 'Sort Order', 'Active']
        for col, header in enumerate(cat_headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header
            cell.font = self.styles.FONTS['header_main']
            cell.fill = self.styles.FILLS['header_secondary']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.border = self.styles.BORDERS['header']
        row += 1

        categories = [
            ('VENDOR', 'Vendor Payments', 1, 'Yes'),
            ('HR', 'Human Resources', 2, 'Yes'),
            ('GOVT', 'Government Payments', 3, 'Yes'),
            ('STRATEGIC', 'Strategic Payments', 4, 'Yes'),
            ('LOAN', 'Loan Repayments', 5, 'Yes'),
            ('OPEX', 'Operating Expenses', 6, 'Yes'),
            ('CAPEX', 'Capital Expenditures', 7, 'Yes'),
            ('UTILITY', 'Utilities', 8, 'Yes'),
            ('OTHER', 'Other Payments', 9, 'Yes'),
        ]

        for cat in categories:
            ws[f'A{row}'] = cat[0]
            ws[f'A{row}'].font = self.styles.FONTS['data_bold']
            ws[f'A{row}'].alignment = self.styles.ALIGNMENTS['center']
            ws[f'A{row}'].border = self.styles.BORDERS['thin']

            ws[f'B{row}'] = cat[1]
            ws[f'B{row}'].font = self.styles.FONTS['data']
            ws[f'B{row}'].border = self.styles.BORDERS['thin']

            ws[f'C{row}'] = cat[2]
            ws[f'C{row}'].font = self.styles.FONTS['data']
            ws[f'C{row}'].alignment = self.styles.ALIGNMENTS['center']
            ws[f'C{row}'].border = self.styles.BORDERS['thin']

            ws[f'D{row}'] = cat[3]
            ws[f'D{row}'].font = self.styles.FONTS['data']
            ws[f'D{row}'].alignment = self.styles.ALIGNMENTS['center']
            ws[f'D{row}'].fill = self.styles.FILLS['status_paid'] if cat[3] == 'Yes' else self.styles.FILLS['row_white']
            ws[f'D{row}'].border = self.styles.BORDERS['thin']
            row += 1

        # Section 5: Named Ranges Reference
        row += 2
        ws.merge_cells(f'A{row}:D{row}')
        ws[f'A{row}'] = 'NAMED RANGES REFERENCE'
        ws[f'A{row}'].font = self.styles.FONTS['header_sub']
        ws[f'A{row}'].fill = self.styles.FILLS['total_row']
        ws[f'A{row}'].border = self.styles.BORDERS['bottom_thick']
        row += 1

        named_ranges = [
            ('cfg_BaseCurrency', 'B4', 'Base currency code'),
            ('cfg_CalendarStart', 'B5', 'Calendar start date'),
            ('cfg_CalendarDays', 'B6', 'Number of calendar days'),
            ('cfg_FiscalYearStart', 'B7', 'Fiscal year start month'),
            ('cfg_WeekStart', 'B8', 'Week start day'),
            ('cfg_OrgName', 'B11', 'Organization name'),
        ]

        for nr in named_ranges:
            ws[f'A{row}'] = nr[0]
            ws[f'A{row}'].font = self.styles.FONTS['data']

            ws[f'B{row}'] = nr[1]
            ws[f'B{row}'].font = self.styles.FONTS['data']
            ws[f'B{row}'].alignment = self.styles.ALIGNMENTS['center']

            ws[f'C{row}'] = nr[2]
            ws[f'C{row}'].font = self.styles.FONTS['small']
            row += 1

        # Column widths
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 15

        # Freeze panes
        ws.freeze_panes = 'A3'

        return self

    def build_fx_rates_sheet(self):
        """Build Exchange Rates lookup table"""
        ws = self.sheets['FX_Rates']

        # Sheet title
        ws.merge_cells('A1:G1')
        ws['A1'] = 'EXCHANGE RATES - CURRENCY CONVERSION TABLE'
        ws['A1'].font = self.styles.FONTS['title']
        ws['A1'].fill = self.styles.FILLS['header_primary']
        ws['A1'].alignment = self.styles.ALIGNMENTS['center']
        ws.row_dimensions[1].height = 35

        # Effective date
        ws['A3'] = 'Effective Date:'
        ws['A3'].font = self.styles.FONTS['category']
        ws['B3'] = datetime.now().strftime('%Y-%m-%d')
        ws['B3'].font = self.styles.FONTS['data_bold']
        ws['B3'].fill = self.styles.FILLS['input_cell']

        # Headers for cross-rate table
        row = 5
        currencies = ['SAR', 'USD', 'AED', 'EUR', 'GBP', 'SGD']

        # Top-left corner label
        ws[f'A{row}'] = 'FROM \\ TO'
        ws[f'A{row}'].font = self.styles.FONTS['header_main']
        ws[f'A{row}'].fill = self.styles.FILLS['header_primary']
        ws[f'A{row}'].alignment = self.styles.ALIGNMENTS['center']
        ws[f'A{row}'].border = self.styles.BORDERS['header']

        # Column headers
        for col, ccy in enumerate(currencies, 2):
            cell = ws.cell(row=row, column=col)
            cell.value = ccy
            cell.font = self.styles.FONTS['header_main']
            cell.fill = self.styles.FILLS['header_primary']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.border = self.styles.BORDERS['header']

        row += 1

        # Exchange rates matrix (rate to convert FROM row currency TO column currency)
        rates_to_sar = {
            'SAR': 1.0000,
            'USD': 3.7500,
            'AED': 1.0210,
            'EUR': 4.1250,
            'GBP': 4.7500,
            'SGD': 2.7800,
        }

        for from_ccy in currencies:
            ws[f'A{row}'] = from_ccy
            ws[f'A{row}'].font = self.styles.FONTS['header_main']
            ws[f'A{row}'].fill = self.styles.FILLS['header_secondary']
            ws[f'A{row}'].alignment = self.styles.ALIGNMENTS['center']
            ws[f'A{row}'].border = self.styles.BORDERS['header']

            for col, to_ccy in enumerate(currencies, 2):
                cell = ws.cell(row=row, column=col)
                # Cross rate calculation: FROM_ccy -> SAR -> TO_ccy
                # rate = rates_to_sar[from_ccy] / rates_to_sar[to_ccy]
                rate = rates_to_sar[from_ccy] / rates_to_sar[to_ccy]
                cell.value = round(rate, 6)
                cell.font = self.styles.FONTS['data']
                cell.number_format = '#,##0.000000'
                cell.alignment = self.styles.ALIGNMENTS['number']
                cell.border = self.styles.BORDERS['thin']

                if from_ccy == to_ccy:
                    cell.fill = self.styles.FILLS['total_row']
                elif row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']

            row += 1

        # Conversion formula helper section
        row += 2
        ws.merge_cells(f'A{row}:G{row}')
        ws[f'A{row}'] = 'CONVERSION FORMULA REFERENCE'
        ws[f'A{row}'].font = self.styles.FONTS['header_sub']
        ws[f'A{row}'].fill = self.styles.FILLS['total_row']
        row += 1

        ws[f'A{row}'] = 'To convert amount to SAR:'
        ws[f'A{row}'].font = self.styles.FONTS['category']
        row += 1
        ws[f'A{row}'] = '=Amount * VLOOKUP(Currency, FX_Rates.$A$6:$B$11, 2, FALSE)'
        ws[f'A{row}'].font = self.styles.FONTS['data']
        ws.merge_cells(f'A{row}:G{row}')

        row += 2
        ws[f'A{row}'] = 'LibreOffice Compatible Formula (with IFERROR):'
        ws[f'A{row}'].font = self.styles.FONTS['category']
        row += 1
        ws[f'A{row}'] = '=IFERROR(Amount * VLOOKUP(Currency, $A$6:$B$11, 2, 0), 0)'
        ws[f'A{row}'].font = self.styles.FONTS['data']
        ws.merge_cells(f'A{row}:G{row}')

        # Column widths
        ws.column_dimensions['A'].width = 15
        for col in range(2, 8):
            ws.column_dimensions[get_column_letter(col)].width = 12

        ws.freeze_panes = 'B6'

        return self

    def _build_source_header(self, ws, title, row=1):
        """Helper to build consistent source sheet headers"""
        ws.merge_cells(f'A{row}:L{row}')
        ws[f'A{row}'] = title
        ws[f'A{row}'].font = self.styles.FONTS['title']
        ws[f'A{row}'].fill = self.styles.FILLS['header_primary']
        ws[f'A{row}'].alignment = self.styles.ALIGNMENTS['center']
        ws.row_dimensions[row].height = 35
        return row + 2

    def _add_column_headers(self, ws, headers, row, start_col=1):
        """Helper to add column headers with consistent styling"""
        for col_offset, header in enumerate(headers):
            cell = ws.cell(row=row, column=start_col + col_offset)
            cell.value = header
            cell.font = self.styles.FONTS['header_main']
            cell.fill = self.styles.FILLS['header_secondary']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.border = self.styles.BORDERS['header']
        return row + 1

    def build_src_collections_sheet(self):
        """Build Source Collections/Receivables sheet"""
        ws = self.sheets['SRC_Collections']

        row = self._build_source_header(ws, 'SOURCE DATA - COLLECTIONS & RECEIVABLES')

        # Column headers
        headers = [
            'Collection ID', 'Customer Name', 'Invoice Ref', 'Description',
            'Original CCY', 'Amount (CCY)', 'Amount (SAR)', 'Expected Date',
            'Collection Type', 'Probability %', 'Status', 'Notes'
        ]
        row = self._add_column_headers(ws, headers, row)

        # Sample data with formulas
        sample_data = [
            ('COL-001', 'Saudi Aramco', 'INV-2024-001', 'Project Payment Milestone 1',
             'SAR', 500000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-15', 'Invoice', 95, 'SCHEDULED', 'Due in 30 days'),
            ('COL-002', 'SABIC', 'INV-2024-002', 'Consulting Services Q4',
             'SAR', 250000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-20', 'Invoice', 90, 'SCHEDULED', ''),
            ('COL-003', 'STC', 'INV-2024-003', 'Technology Implementation',
             'USD', 150000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-25', 'Invoice', 85, 'PENDING', 'Awaiting approval'),
            ('COL-004', 'Almarai', 'INV-2024-004', 'Annual Maintenance Contract',
             'SAR', 180000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-05', 'Contract', 100, 'SCHEDULED', 'Recurring'),
            ('COL-005', 'Mobily', 'INV-2024-005', 'Network Services',
             'EUR', 75000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-10', 'Invoice', 80, 'PENDING', ''),
        ]

        for data in sample_data:
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                if isinstance(value, str) and value.startswith('='):
                    cell.value = value.format(r=row)
                elif col == 8:  # Date column - convert to actual date
                    cell.value = parse_date(value)
                    cell.number_format = 'YYYY-MM-DD'
                else:
                    cell.value = value

                cell.font = self.styles.FONTS['data']
                cell.border = self.styles.BORDERS['thin']
                cell.alignment = self.styles.ALIGNMENTS['center'] if col in [1, 5, 9, 10, 11] else self.styles.ALIGNMENTS['left']

                if col in [6, 7]:  # Currency columns
                    cell.number_format = '#,##0.00'
                    cell.alignment = self.styles.ALIGNMENTS['number']

                if row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']

            row += 1

        # Add 20 empty input rows
        for _ in range(20):
            for col in range(1, 13):
                cell = ws.cell(row=row, column=col)
                cell.border = self.styles.BORDERS['thin']
                cell.fill = self.styles.FILLS['input_cell'] if col in [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12] else self.styles.FILLS['row_white']
                if col == 7:  # SAR formula column
                    cell.value = f'=IFERROR(IF(F{row}="","",F{row}*VLOOKUP(E{row},FX_Rates.$A$6:$B$11,2,0)),0)'
                    cell.number_format = '#,##0.00'
            row += 1

        # Column widths
        col_widths = [12, 20, 15, 30, 12, 15, 15, 12, 15, 12, 12, 25]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.freeze_panes = 'A4'
        return self

    def build_src_opex_sheet(self):
        """Build Source Operating Expenditures sheet"""
        ws = self.sheets['SRC_OPeX']

        row = self._build_source_header(ws, 'SOURCE DATA - OPERATING EXPENDITURES (OPeX)')

        headers = [
            'OPeX ID', 'Vendor/Payee', 'Category', 'Description',
            'Original CCY', 'Amount (CCY)', 'Amount (SAR)', 'Due Date',
            'Payment Type', 'Frequency', 'Status', 'Notes'
        ]
        row = self._add_column_headers(ws, headers, row)

        sample_data = [
            ('OPX-001', 'Saudi Electricity Co', 'Utilities', 'Monthly Electricity',
             'SAR', 45000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-15', 'Recurring', 'Monthly', 'PENDING', 'HQ Building'),
            ('OPX-002', 'Saudi Telecom', 'Telecom', 'Internet & Phone Services',
             'SAR', 15000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-20', 'Recurring', 'Monthly', 'SCHEDULED', ''),
            ('OPX-003', 'Office Rent LLC', 'Rent', 'Office Space Rental',
             'SAR', 120000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-25', 'Recurring', 'Monthly', 'SCHEDULED', 'Main Office'),
            ('OPX-004', 'Insurance Corp', 'Insurance', 'Property Insurance Premium',
             'SAR', 85000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-01', 'Recurring', 'Quarterly', 'PENDING', 'Q1 Payment'),
            ('OPX-005', 'Security Services', 'Security', 'Building Security',
             'SAR', 35000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-05', 'Recurring', 'Monthly', 'SCHEDULED', ''),
        ]

        for data in sample_data:
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                if isinstance(value, str) and value.startswith('='):
                    cell.value = value.format(r=row)
                else:
                    cell.value = value
                cell.font = self.styles.FONTS['data']
                cell.border = self.styles.BORDERS['thin']
                if col in [6, 7]:
                    cell.number_format = '#,##0.00'
                    cell.alignment = self.styles.ALIGNMENTS['number']
                if row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']
            row += 1

        # Empty input rows
        for _ in range(20):
            for col in range(1, 13):
                cell = ws.cell(row=row, column=col)
                cell.border = self.styles.BORDERS['thin']
                cell.fill = self.styles.FILLS['input_cell'] if col != 7 else self.styles.FILLS['row_white']
                if col == 7:
                    cell.value = f'=IFERROR(IF(F{row}="","",F{row}*VLOOKUP(E{row},FX_Rates.$A$6:$B$11,2,0)),0)'
                    cell.number_format = '#,##0.00'
            row += 1

        col_widths = [12, 22, 15, 30, 12, 15, 15, 12, 15, 12, 12, 25]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.freeze_panes = 'A4'
        return self

    def build_src_capex_sheet(self):
        """Build Source Capital Expenditures sheet"""
        ws = self.sheets['SRC_CAPEX']

        row = self._build_source_header(ws, 'SOURCE DATA - CAPITAL EXPENDITURES (CAPEX)')

        headers = [
            'CAPEX ID', 'Project Name', 'Vendor', 'Description',
            'Original CCY', 'Amount (CCY)', 'Amount (SAR)', 'Payment Date',
            'Project Phase', 'Budget Code', 'Status', 'Approval Ref'
        ]
        row = self._add_column_headers(ws, headers, row)

        sample_data = [
            ('CAP-001', 'IT Infrastructure', 'Dell Technologies', 'Server Equipment',
             'USD', 250000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-18', 'Phase 1', 'CAPEX-IT-001', 'PENDING', 'APR-2024-156'),
            ('CAP-002', 'Office Expansion', 'Saudi Contractors', 'Building Renovation',
             'SAR', 1500000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-28', 'Phase 2', 'CAPEX-FAC-002', 'SCHEDULED', 'APR-2024-178'),
            ('CAP-003', 'Vehicle Fleet', 'Toyota KSA', 'Fleet Vehicles Purchase',
             'SAR', 450000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-15', 'Phase 1', 'CAPEX-VEH-001', 'PENDING', 'APR-2024-192'),
            ('CAP-004', 'Software License', 'SAP SE', 'ERP Implementation',
             'EUR', 180000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-20', 'Phase 1', 'CAPEX-IT-003', 'SCHEDULED', 'APR-2024-201'),
        ]

        for data in sample_data:
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                if isinstance(value, str) and value.startswith('='):
                    cell.value = value.format(r=row)
                else:
                    cell.value = value
                cell.font = self.styles.FONTS['data']
                cell.border = self.styles.BORDERS['thin']
                if col in [6, 7]:
                    cell.number_format = '#,##0.00'
                    cell.alignment = self.styles.ALIGNMENTS['number']
                if row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']
            row += 1

        for _ in range(15):
            for col in range(1, 13):
                cell = ws.cell(row=row, column=col)
                cell.border = self.styles.BORDERS['thin']
                cell.fill = self.styles.FILLS['input_cell'] if col != 7 else self.styles.FILLS['row_white']
                if col == 7:
                    cell.value = f'=IFERROR(IF(F{row}="","",F{row}*VLOOKUP(E{row},FX_Rates.$A$6:$B$11,2,0)),0)'
                    cell.number_format = '#,##0.00'
            row += 1

        col_widths = [12, 20, 20, 28, 12, 15, 15, 12, 12, 15, 12, 15]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.freeze_panes = 'A4'
        return self

    def build_src_hr_sheet(self):
        """Build Source Human Resources/Payroll sheet"""
        ws = self.sheets['SRC_HR']

        row = self._build_source_header(ws, 'SOURCE DATA - HUMAN RESOURCES & PAYROLL')

        headers = [
            'HR ID', 'Payment Type', 'Department', 'Description',
            'Original CCY', 'Amount (CCY)', 'Amount (SAR)', 'Payment Date',
            'Pay Period', 'Employee Count', 'Status', 'Notes'
        ]
        row = self._add_column_headers(ws, headers, row)

        sample_data = [
            ('HR-001', 'Salaries', 'All Departments', 'Monthly Salaries - Dec 2024',
             'SAR', 2500000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-25', 'Dec-2024', 150, 'SCHEDULED', 'Regular payroll'),
            ('HR-002', 'GOSI', 'All Departments', 'GOSI Contributions',
             'SAR', 375000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-15', 'Dec-2024', 150, 'PENDING', 'Government mandatory'),
            ('HR-003', 'Medical Insurance', 'All Departments', 'Group Medical Insurance',
             'SAR', 180000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-20', 'Q1-2025', 150, 'SCHEDULED', 'Quarterly premium'),
            ('HR-004', 'End of Service', 'Operations', 'EOS Provisions',
             'SAR', 95000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-05', 'Dec-2024', 5, 'PENDING', 'Resignations'),
            ('HR-005', 'Bonuses', 'Sales', 'Q4 Performance Bonuses',
             'SAR', 450000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-15', 'Q4-2024', 45, 'SCHEDULED', 'Sales team'),
            ('HR-006', 'Training', 'IT', 'Technical Training Program',
             'USD', 25000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-20', 'Q1-2025', 20, 'PENDING', 'External training'),
        ]

        for data in sample_data:
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                if isinstance(value, str) and value.startswith('='):
                    cell.value = value.format(r=row)
                else:
                    cell.value = value
                cell.font = self.styles.FONTS['data']
                cell.border = self.styles.BORDERS['thin']
                if col in [6, 7]:
                    cell.number_format = '#,##0.00'
                    cell.alignment = self.styles.ALIGNMENTS['number']
                if row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']
            row += 1

        for _ in range(20):
            for col in range(1, 13):
                cell = ws.cell(row=row, column=col)
                cell.border = self.styles.BORDERS['thin']
                cell.fill = self.styles.FILLS['input_cell'] if col != 7 else self.styles.FILLS['row_white']
                if col == 7:
                    cell.value = f'=IFERROR(IF(F{row}="","",F{row}*VLOOKUP(E{row},FX_Rates.$A$6:$B$11,2,0)),0)'
                    cell.number_format = '#,##0.00'
            row += 1

        col_widths = [12, 18, 18, 30, 12, 15, 15, 12, 12, 14, 12, 25]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.freeze_panes = 'A4'
        return self

    def build_src_debt_sheet(self):
        """Build Source Debt Service/Loans sheet"""
        ws = self.sheets['SRC_Debt']

        row = self._build_source_header(ws, 'SOURCE DATA - DEBT SERVICE & LOAN OBLIGATIONS')

        headers = [
            'Loan ID', 'Bank/Lender', 'Facility Type', 'Description',
            'Original CCY', 'Principal (CCY)', 'Interest (CCY)', 'Total (SAR)',
            'Payment Date', 'Outstanding Balance', 'Status', 'Maturity Date'
        ]
        row = self._add_column_headers(ws, headers, row)

        sample_data = [
            ('LN-001', 'Saudi National Bank', 'Term Loan', 'Working Capital Facility',
             'SAR', 500000.00, 25000.00, '=IFERROR((F{r}+G{r})*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-15', 4500000.00, 'SCHEDULED', '2026-12-15'),
            ('LN-002', 'Al Rajhi Bank', 'Islamic Finance', 'Murabaha Facility',
             'SAR', 350000.00, 18000.00, '=IFERROR((F{r}+G{r})*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-20', 3200000.00, 'PENDING', '2027-06-20'),
            ('LN-003', 'HSBC', 'Revolving Credit', 'USD Credit Line',
             'USD', 200000.00, 8500.00, '=IFERROR((F{r}+G{r})*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-28', 1800000.00, 'SCHEDULED', '2025-12-28'),
            ('LN-004', 'Riyad Bank', 'Equipment Finance', 'Vehicle Lease',
             'SAR', 85000.00, 4200.00, '=IFERROR((F{r}+G{r})*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-05', 680000.00, 'SCHEDULED', '2026-01-05'),
            ('LN-005', 'Emirates NBD', 'Trade Finance', 'LC Facility',
             'AED', 450000.00, 15000.00, '=IFERROR((F{r}+G{r})*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-10', 2700000.00, 'PENDING', '2025-07-10'),
        ]

        for data in sample_data:
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                if isinstance(value, str) and value.startswith('='):
                    cell.value = value.format(r=row)
                else:
                    cell.value = value
                cell.font = self.styles.FONTS['data']
                cell.border = self.styles.BORDERS['thin']
                if col in [6, 7, 8, 10]:
                    cell.number_format = '#,##0.00'
                    cell.alignment = self.styles.ALIGNMENTS['number']
                if row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']
            row += 1

        for _ in range(15):
            for col in range(1, 13):
                cell = ws.cell(row=row, column=col)
                cell.border = self.styles.BORDERS['thin']
                cell.fill = self.styles.FILLS['input_cell'] if col != 8 else self.styles.FILLS['row_white']
                if col == 8:
                    cell.value = f'=IFERROR(IF(F{row}="","",IF(G{row}="",(F{row})*VLOOKUP(E{row},FX_Rates.$A$6:$B$11,2,0),(F{row}+G{row})*VLOOKUP(E{row},FX_Rates.$A$6:$B$11,2,0))),0)'
                    cell.number_format = '#,##0.00'
            row += 1

        col_widths = [12, 20, 16, 25, 12, 15, 15, 15, 12, 18, 12, 12]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.freeze_panes = 'A4'
        return self

    def build_src_fixed_sheet(self):
        """Build Source Fixed Expenses sheet"""
        ws = self.sheets['SRC_Fixed']

        row = self._build_source_header(ws, 'SOURCE DATA - FIXED EXPENSES')

        headers = [
            'Fixed ID', 'Vendor/Payee', 'Expense Type', 'Description',
            'Original CCY', 'Amount (CCY)', 'Amount (SAR)', 'Due Date',
            'Frequency', 'Contract End', 'Status', 'Auto-Renew'
        ]
        row = self._add_column_headers(ws, headers, row)

        sample_data = [
            ('FIX-001', 'Property Management', 'Lease', 'Main Office Rent',
             'SAR', 150000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-01', 'Monthly', '2025-12-31', 'PAID', 'Yes'),
            ('FIX-002', 'Software Vendor', 'License', 'Microsoft 365 Enterprise',
             'USD', 12000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-15', 'Monthly', '2025-12-31', 'SCHEDULED', 'Yes'),
            ('FIX-003', 'Security Company', 'Service', 'Building Security Contract',
             'SAR', 45000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-20', 'Monthly', '2025-06-30', 'SCHEDULED', 'No'),
            ('FIX-004', 'Cleaning Services', 'Service', 'Office Cleaning',
             'SAR', 18000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-25', 'Monthly', '2025-12-31', 'PENDING', 'Yes'),
        ]

        for data in sample_data:
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                if isinstance(value, str) and value.startswith('='):
                    cell.value = value.format(r=row)
                else:
                    cell.value = value
                cell.font = self.styles.FONTS['data']
                cell.border = self.styles.BORDERS['thin']
                if col in [6, 7]:
                    cell.number_format = '#,##0.00'
                    cell.alignment = self.styles.ALIGNMENTS['number']
                if row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']
            row += 1

        for _ in range(15):
            for col in range(1, 13):
                cell = ws.cell(row=row, column=col)
                cell.border = self.styles.BORDERS['thin']
                cell.fill = self.styles.FILLS['input_cell'] if col != 7 else self.styles.FILLS['row_white']
                if col == 7:
                    cell.value = f'=IFERROR(IF(F{row}="","",F{row}*VLOOKUP(E{row},FX_Rates.$A$6:$B$11,2,0)),0)'
                    cell.number_format = '#,##0.00'
            row += 1

        col_widths = [12, 22, 15, 28, 12, 15, 15, 12, 12, 12, 12, 12]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.freeze_panes = 'A4'
        return self

    def build_src_variable_sheet(self):
        """Build Source Variable Expenses sheet"""
        ws = self.sheets['SRC_Variable']

        row = self._build_source_header(ws, 'SOURCE DATA - VARIABLE EXPENSES')

        headers = [
            'Var ID', 'Vendor/Payee', 'Expense Type', 'Description',
            'Original CCY', 'Amount (CCY)', 'Amount (SAR)', 'Due Date',
            'Cost Center', 'Budget Code', 'Status', 'Approval Ref'
        ]
        row = self._add_column_headers(ws, headers, row)

        sample_data = [
            ('VAR-001', 'Travel Agency', 'Travel', 'Business Travel - Dec',
             'SAR', 35000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-18', 'CC-SALES', 'BUD-TRV-001', 'PENDING', 'APR-TRV-089'),
            ('VAR-002', 'Catering Co', 'Events', 'Year End Event Catering',
             'SAR', 75000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-22', 'CC-HR', 'BUD-EVT-002', 'SCHEDULED', 'APR-EVT-045'),
            ('VAR-003', 'Marketing Agency', 'Marketing', 'Q1 Campaign Materials',
             'SAR', 125000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-05', 'CC-MKT', 'BUD-MKT-003', 'PENDING', 'APR-MKT-112'),
            ('VAR-004', 'Consultant LLC', 'Consulting', 'Strategy Consulting',
             'GBP', 28000.00, '=IFERROR(F{r}*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-10', 'CC-EXEC', 'BUD-CON-001', 'SCHEDULED', 'APR-CON-078'),
        ]

        for data in sample_data:
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                if isinstance(value, str) and value.startswith('='):
                    cell.value = value.format(r=row)
                else:
                    cell.value = value
                cell.font = self.styles.FONTS['data']
                cell.border = self.styles.BORDERS['thin']
                if col in [6, 7]:
                    cell.number_format = '#,##0.00'
                    cell.alignment = self.styles.ALIGNMENTS['number']
                if row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']
            row += 1

        for _ in range(20):
            for col in range(1, 13):
                cell = ws.cell(row=row, column=col)
                cell.border = self.styles.BORDERS['thin']
                cell.fill = self.styles.FILLS['input_cell'] if col != 7 else self.styles.FILLS['row_white']
                if col == 7:
                    cell.value = f'=IFERROR(IF(F{row}="","",F{row}*VLOOKUP(E{row},FX_Rates.$A$6:$B$11,2,0)),0)'
                    cell.number_format = '#,##0.00'
            row += 1

        col_widths = [12, 22, 15, 28, 12, 15, 15, 12, 12, 14, 12, 14]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.freeze_panes = 'A4'
        return self

    def build_src_deposits_sheet(self):
        """Build Source Deposit Maturities sheet"""
        ws = self.sheets['SRC_Deposits']

        row = self._build_source_header(ws, 'SOURCE DATA - DEPOSIT MATURITIES & INVESTMENTS')

        headers = [
            'Deposit ID', 'Bank/Institution', 'Instrument Type', 'Description',
            'Original CCY', 'Principal (CCY)', 'Interest (CCY)', 'Total (SAR)',
            'Maturity Date', 'Term (Days)', 'Rate %', 'Auto-Rollover'
        ]
        row = self._add_column_headers(ws, headers, row)

        sample_data = [
            ('DEP-001', 'Saudi National Bank', 'Time Deposit', '90-Day TD',
             'SAR', 5000000.00, 62500.00, '=IFERROR((F{r}+G{r})*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-20', 90, 5.00, 'No'),
            ('DEP-002', 'Al Rajhi Bank', 'Mudaraba', 'Islamic Investment Account',
             'SAR', 3000000.00, 45000.00, '=IFERROR((F{r}+G{r})*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2024-12-28', 180, 6.00, 'Yes'),
            ('DEP-003', 'HSBC', 'Money Market', 'USD Money Market Fund',
             'USD', 1000000.00, 12500.00, '=IFERROR((F{r}+G{r})*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-15', 60, 5.00, 'Yes'),
            ('DEP-004', 'Riyad Bank', 'Sukuk', 'Government Sukuk',
             'SAR', 2500000.00, 75000.00, '=IFERROR((F{r}+G{r})*VLOOKUP(E{r},FX_Rates.$A$6:$B$11,2,0),0)',
             '2025-01-30', 365, 6.00, 'No'),
        ]

        for data in sample_data:
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                if isinstance(value, str) and value.startswith('='):
                    cell.value = value.format(r=row)
                else:
                    cell.value = value
                cell.font = self.styles.FONTS['data']
                cell.border = self.styles.BORDERS['thin']
                if col in [6, 7, 8]:
                    cell.number_format = '#,##0.00'
                    cell.alignment = self.styles.ALIGNMENTS['number']
                if col == 11:
                    cell.number_format = '0.00%'
                if row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']
            row += 1

        for _ in range(15):
            for col in range(1, 13):
                cell = ws.cell(row=row, column=col)
                cell.border = self.styles.BORDERS['thin']
                cell.fill = self.styles.FILLS['input_cell'] if col != 8 else self.styles.FILLS['row_white']
                if col == 8:
                    cell.value = f'=IFERROR(IF(F{row}="","",IF(G{row}="",(F{row})*VLOOKUP(E{row},FX_Rates.$A$6:$B$11,2,0),(F{row}+G{row})*VLOOKUP(E{row},FX_Rates.$A$6:$B$11,2,0))),0)'
                    cell.number_format = '#,##0.00'
            row += 1

        col_widths = [12, 20, 16, 22, 12, 18, 15, 18, 12, 12, 10, 12]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.freeze_panes = 'A4'
        return self

    def build_vendor_master_sheet(self):
        """Build Vendor/Payee Master List - Single source of truth for all vendors"""
        ws = self.sheets['Vendor_Master']

        row = self._build_source_header(ws, 'VENDOR & PAYEE MASTER LIST')

        headers = [
            'Vendor ID', 'Vendor Name', 'Category', 'Sub-Category',
            'Contact Person', 'Email', 'Phone', 'Bank Name',
            'Account Number', 'IBAN', 'Default CCY', 'Payment Terms',
            'Active', 'Sort Order'
        ]
        row = self._add_column_headers(ws, headers, row)

        # Comprehensive vendor master data organized by category
        vendor_data = [
            # VENDOR PAYMENTS
            ('VND-001', 'Saudi Electricity Company', 'VENDOR', 'Utilities', 'Finance Dept', 'billing@sec.com.sa', '+966-11-123-4567', 'Saudi National Bank', '1234567890', 'SA1234567890123456789012', 'SAR', 'Net 30', 'Yes', 1),
            ('VND-002', 'Saudi Telecom (STC)', 'VENDOR', 'Telecom', 'Corporate Sales', 'corporate@stc.com.sa', '+966-11-234-5678', 'Al Rajhi Bank', '2345678901', 'SA2345678901234567890123', 'SAR', 'Net 15', 'Yes', 2),
            ('VND-003', 'Water Authority', 'VENDOR', 'Utilities', 'Collections', 'billing@nwc.com.sa', '+966-11-345-6789', 'Riyad Bank', '3456789012', 'SA3456789012345678901234', 'SAR', 'Net 30', 'Yes', 3),
            ('VND-004', 'Dell Technologies', 'VENDOR', 'IT Equipment', 'Account Manager', 'sales@dell.com', '+971-4-456-7890', 'Citibank', '4567890123', 'AE4567890123456789012345', 'USD', 'Net 45', 'Yes', 4),
            ('VND-005', 'Microsoft Corporation', 'VENDOR', 'Software', 'Licensing', 'licensing@microsoft.com', '+1-800-642-7676', 'JPMorgan Chase', '5678901234', 'US56789012345678901234', 'USD', 'Annual', 'Yes', 5),
            ('VND-006', 'Office Supplies Co', 'VENDOR', 'Office Supplies', 'Sales', 'sales@officesupplies.sa', '+966-11-567-8901', 'Saudi National Bank', '6789012345', 'SA6789012345678901234567', 'SAR', 'Net 15', 'Yes', 6),

            # HR PAYMENTS
            ('HR-001', 'Monthly Payroll', 'HR', 'Salaries', 'HR Director', 'hr@company.com', '+966-11-100-0001', 'Internal', 'PAYROLL', 'N/A', 'SAR', 'Monthly', 'Yes', 10),
            ('HR-002', 'GOSI (General Organization for Social Insurance)', 'HR', 'Social Insurance', 'GOSI Portal', 'employer@gosi.gov.sa', '+966-11-800-1234', 'GOSI', 'GOSI-EMP', 'SA0000000000GOSI', 'SAR', 'Monthly', 'Yes', 11),
            ('HR-003', 'Medical Insurance Provider', 'HR', 'Benefits', 'Account Manager', 'corporate@bupa.com.sa', '+966-11-200-0002', 'Al Rajhi Bank', '7890123456', 'SA7890123456789012345678', 'SAR', 'Quarterly', 'Yes', 12),
            ('HR-004', 'End of Service Provisions', 'HR', 'EOS', 'HR Director', 'hr@company.com', '+966-11-100-0001', 'Internal', 'EOS-PROV', 'N/A', 'SAR', 'On Demand', 'Yes', 13),
            ('HR-005', 'Staff Bonuses', 'HR', 'Bonuses', 'HR Director', 'hr@company.com', '+966-11-100-0001', 'Internal', 'BONUS', 'N/A', 'SAR', 'Quarterly', 'Yes', 14),
            ('HR-006', 'Training Provider', 'HR', 'Training', 'Training Coord', 'training@provider.com', '+966-11-300-0003', 'Saudi National Bank', '8901234567', 'SA8901234567890123456789', 'SAR', 'Per Course', 'Yes', 15),

            # GOVERNMENT PAYMENTS
            ('GOV-001', 'Zakat, Tax and Customs Authority', 'GOVT', 'Tax', 'ZATCA Portal', 'support@zatca.gov.sa', '+966-11-400-0004', 'SAMA', 'ZATCA-TAX', 'SA0000000000ZATCA', 'SAR', 'As Due', 'Yes', 20),
            ('GOV-002', 'Ministry of Labor', 'GOVT', 'Labor Fees', 'MOL Portal', 'support@mol.gov.sa', '+966-11-400-0005', 'SAMA', 'MOL-FEES', 'SA0000000000MOL', 'SAR', 'As Due', 'Yes', 21),
            ('GOV-003', 'Municipality Fees', 'GOVT', 'Municipal', 'Municipality', 'fees@riyadh.gov.sa', '+966-11-400-0006', 'SAMA', 'MUNI-FEES', 'SA0000000000MUNI', 'SAR', 'Annual', 'Yes', 22),
            ('GOV-004', 'Chamber of Commerce', 'GOVT', 'Registration', 'CoC Portal', 'membership@coc.org.sa', '+966-11-400-0007', 'Saudi National Bank', '9012345678', 'SA9012345678901234567890', 'SAR', 'Annual', 'Yes', 23),

            # STRATEGIC PAYMENTS
            ('STR-001', 'Strategic Partner Alpha', 'STRATEGIC', 'Partnership', 'CEO Office', 'ceo@partneralpha.com', '+971-4-500-0001', 'Emirates NBD', '0123456789', 'AE0123456789012345678901', 'AED', 'Milestone', 'Yes', 30),
            ('STR-002', 'Investment Fund Beta', 'STRATEGIC', 'Investment', 'Fund Manager', 'invest@fundbeta.com', '+44-20-600-0002', 'Barclays', '1234567890AB', 'GB1234567890123456789012', 'GBP', 'Quarterly', 'Yes', 31),
            ('STR-003', 'JV Company Gamma', 'STRATEGIC', 'Joint Venture', 'JV Director', 'jv@gamma.com', '+65-700-0003', 'DBS Bank', '2345678901CD', 'SG2345678901234567890123', 'SGD', 'Monthly', 'Yes', 32),
            ('STR-004', 'Acquisition Target Delta', 'STRATEGIC', 'M&A', 'M&A Advisor', 'ma@delta.com', '+49-800-0004', 'Deutsche Bank', '3456789012EF', 'DE3456789012345678901234', 'EUR', 'Milestone', 'Yes', 33),

            # LOAN PAYMENTS (Banks)
            ('LOAN-001', 'Saudi National Bank', 'LOAN', 'Term Loan', 'Relationship Mgr', 'corporate@snb.com.sa', '+966-11-600-0001', 'Saudi National Bank', 'LOAN-SNB-001', 'SA0000000000SNB001', 'SAR', 'Monthly', 'Yes', 40),
            ('LOAN-002', 'Al Rajhi Bank', 'LOAN', 'Islamic Finance', 'Relationship Mgr', 'corporate@alrajhi.com.sa', '+966-11-600-0002', 'Al Rajhi Bank', 'LOAN-ARB-001', 'SA0000000000ARB001', 'SAR', 'Monthly', 'Yes', 41),
            ('LOAN-003', 'HSBC Saudi Arabia', 'LOAN', 'Revolving Credit', 'Relationship Mgr', 'corporate@hsbc.com.sa', '+966-11-600-0003', 'HSBC', 'LOAN-HSBC-001', 'SA0000000000HSBC01', 'USD', 'Monthly', 'Yes', 42),
            ('LOAN-004', 'Riyad Bank', 'LOAN', 'Equipment Finance', 'Relationship Mgr', 'corporate@riyadbank.com', '+966-11-600-0004', 'Riyad Bank', 'LOAN-RYD-001', 'SA0000000000RYD001', 'SAR', 'Monthly', 'Yes', 43),
            ('LOAN-005', 'Emirates NBD', 'LOAN', 'Trade Finance', 'Trade Finance', 'trade@emiratesnbd.com', '+971-4-600-0005', 'Emirates NBD', 'LOAN-ENBD-001', 'AE0000000000ENBD01', 'AED', 'As Due', 'Yes', 44),

            # OTHER OPERATIONAL
            ('OPS-001', 'Property Management Co', 'OPEX', 'Rent', 'Property Mgr', 'rent@property.sa', '+966-11-700-0001', 'Saudi National Bank', '4567890123GH', 'SA4567890123456789012345', 'SAR', 'Monthly', 'Yes', 50),
            ('OPS-002', 'Security Services Co', 'OPEX', 'Security', 'Operations', 'ops@security.sa', '+966-11-700-0002', 'Riyad Bank', '5678901234IJ', 'SA5678901234567890123456', 'SAR', 'Monthly', 'Yes', 51),
            ('OPS-003', 'Cleaning Services Co', 'OPEX', 'Facility', 'Operations', 'ops@cleaning.sa', '+966-11-700-0003', 'Al Rajhi Bank', '6789012345KL', 'SA6789012345678901234567', 'SAR', 'Monthly', 'Yes', 52),
            ('OPS-004', 'Insurance Corporation', 'OPEX', 'Insurance', 'Account Mgr', 'corporate@insurance.sa', '+966-11-700-0004', 'Saudi National Bank', '7890123456MN', 'SA7890123456789012345678', 'SAR', 'Quarterly', 'Yes', 53),
        ]

        for data in vendor_data:
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                cell.value = value
                cell.font = self.styles.FONTS['data']
                cell.border = self.styles.BORDERS['thin']
                cell.alignment = self.styles.ALIGNMENTS['center'] if col in [1, 3, 4, 11, 12, 13, 14] else self.styles.ALIGNMENTS['left']

                if row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']

                # Category-based color coding
                if col == 3:
                    category = value
                    if category == 'VENDOR':
                        cell.fill = PatternFill(start_color='E3F2FD', end_color='E3F2FD', fill_type='solid')
                    elif category == 'HR':
                        cell.fill = PatternFill(start_color='E8F5E9', end_color='E8F5E9', fill_type='solid')
                    elif category == 'GOVT':
                        cell.fill = PatternFill(start_color='FFF3E0', end_color='FFF3E0', fill_type='solid')
                    elif category == 'STRATEGIC':
                        cell.fill = PatternFill(start_color='F3E5F5', end_color='F3E5F5', fill_type='solid')
                    elif category == 'LOAN':
                        cell.fill = PatternFill(start_color='FFEBEE', end_color='FFEBEE', fill_type='solid')
                    elif category == 'OPEX':
                        cell.fill = PatternFill(start_color='E0F7FA', end_color='E0F7FA', fill_type='solid')

            row += 1

        # Empty input rows
        for _ in range(20):
            for col in range(1, 15):
                cell = ws.cell(row=row, column=col)
                cell.border = self.styles.BORDERS['thin']
                cell.fill = self.styles.FILLS['input_cell']
            row += 1

        col_widths = [12, 35, 12, 18, 18, 25, 18, 20, 18, 28, 12, 12, 8, 10]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.freeze_panes = 'C4'
        return self

    def build_payment_data_sheet(self):
        """Build Payment Data sheet - SINGLE SOURCE OF TRUTH for all payments"""
        ws = self.sheets['Payment_Data']

        row = self._build_source_header(ws, 'PAYMENT DATA - SINGLE SOURCE OF TRUTH')

        # Add note about this being the master data source
        ws.merge_cells(f'A{row}:P{row}')
        ws[f'A{row}'] = '⚠ THIS IS THE MASTER PAYMENT DATA SOURCE - All calendars reference this sheet'
        ws[f'A{row}'].font = Font(name='Calibri', size=11, bold=True, color='C62828')
        ws[f'A{row}'].fill = PatternFill(start_color='FFEBEE', end_color='FFEBEE', fill_type='solid')
        ws[f'A{row}'].alignment = self.styles.ALIGNMENTS['center']
        row += 2

        headers = [
            'Payment ID', 'Vendor ID', 'Vendor Name', 'Category', 'Sub-Category',
            'Description', 'Original CCY', 'Amount (CCY)', 'Amount (SAR)',
            'Due Date', 'Maturity Date', 'Status', 'Payment Date', 'Reference',
            'Priority', 'Notes'
        ]
        row = self._add_column_headers(ws, headers, row)

        # Comprehensive payment data samples covering all categories
        payment_data = [
            # VENDOR PAYMENTS
            ('PAY-001', 'VND-001', 'Saudi Electricity Company', 'VENDOR', 'Utilities', 'Monthly Electricity - Dec 2024', 'SAR', 45000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-15', '2024-12-15', 'PENDING', '', 'ELEC-DEC-2024', 2, 'HQ Building'),
            ('PAY-002', 'VND-002', 'Saudi Telecom (STC)', 'VENDOR', 'Telecom', 'Internet Services - Dec 2024', 'SAR', 15000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-20', '2024-12-20', 'SCHEDULED', '', 'STC-DEC-2024', 3, ''),
            ('PAY-003', 'VND-004', 'Dell Technologies', 'VENDOR', 'IT Equipment', 'Server Equipment Purchase', 'USD', 250000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-18', '2024-12-18', 'PENDING', '', 'DELL-PO-2024-156', 1, 'CAPEX - IT Infrastructure'),
            ('PAY-004', 'VND-006', 'Office Supplies Co', 'VENDOR', 'Office Supplies', 'Q4 Office Supplies', 'SAR', 8500.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-22', '2024-12-22', 'PAID', '2024-12-10', 'OFF-Q4-2024', 4, ''),

            # HR PAYMENTS
            ('PAY-005', 'HR-001', 'Monthly Payroll', 'HR', 'Salaries', 'December 2024 Salaries', 'SAR', 2500000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-25', '2024-12-25', 'SCHEDULED', '', 'PAY-DEC-2024', 1, '150 Employees'),
            ('PAY-006', 'HR-002', 'GOSI (General Organization for Social Insurance)', 'HR', 'Social Insurance', 'GOSI Contributions - Dec 2024', 'SAR', 375000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-15', '2024-12-15', 'PENDING', '', 'GOSI-DEC-2024', 1, 'Government mandatory'),
            ('PAY-007', 'HR-003', 'Medical Insurance Provider', 'HR', 'Benefits', 'Q1 2025 Medical Insurance', 'SAR', 180000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-20', '2024-12-20', 'SCHEDULED', '', 'MED-Q1-2025', 2, 'Quarterly premium'),
            ('PAY-008', 'HR-005', 'Staff Bonuses', 'HR', 'Bonuses', 'Q4 2024 Performance Bonuses', 'SAR', 450000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-15', '2025-01-15', 'SCHEDULED', '', 'BONUS-Q4-2024', 2, 'Sales team'),

            # GOVERNMENT PAYMENTS
            ('PAY-009', 'GOV-001', 'Zakat, Tax and Customs Authority', 'GOVT', 'Tax', 'Q4 2024 VAT Payment', 'SAR', 285000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-31', '2024-12-31', 'PENDING', '', 'VAT-Q4-2024', 1, 'Quarterly VAT'),
            ('PAY-010', 'GOV-002', 'Ministry of Labor', 'GOVT', 'Labor Fees', 'Work Permit Renewals', 'SAR', 125000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-10', '2025-01-10', 'PENDING', '', 'MOL-WP-2025', 2, '25 permits'),
            ('PAY-011', 'GOV-003', 'Municipality Fees', 'GOVT', 'Municipal', 'Annual Business License', 'SAR', 45000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-05', '2025-01-05', 'SCHEDULED', '', 'MUNI-2025', 3, 'Annual renewal'),

            # STRATEGIC PAYMENTS
            ('PAY-012', 'STR-001', 'Strategic Partner Alpha', 'STRATEGIC', 'Partnership', 'Partnership Milestone Payment', 'AED', 500000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-28', '2024-12-28', 'SCHEDULED', '', 'ALPHA-M3-2024', 1, 'Milestone 3'),
            ('PAY-013', 'STR-002', 'Investment Fund Beta', 'STRATEGIC', 'Investment', 'Q4 Investment Commitment', 'GBP', 150000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-20', '2025-01-20', 'PENDING', '', 'BETA-Q4-2024', 2, 'Capital call'),
            ('PAY-014', 'STR-003', 'JV Company Gamma', 'STRATEGIC', 'Joint Venture', 'Monthly JV Contribution', 'SGD', 75000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-05', '2025-01-05', 'SCHEDULED', '', 'GAMMA-JAN-2025', 3, 'Monthly'),

            # LOAN PAYMENTS
            ('PAY-015', 'LOAN-001', 'Saudi National Bank', 'LOAN', 'Term Loan', 'Working Capital - Principal + Interest', 'SAR', 525000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-15', '2024-12-15', 'SCHEDULED', '', 'SNB-DEC-2024', 1, 'Monthly installment'),
            ('PAY-016', 'LOAN-002', 'Al Rajhi Bank', 'LOAN', 'Islamic Finance', 'Murabaha Payment', 'SAR', 368000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-20', '2024-12-20', 'PENDING', '', 'ARB-DEC-2024', 1, 'Profit + Principal'),
            ('PAY-017', 'LOAN-003', 'HSBC Saudi Arabia', 'LOAN', 'Revolving Credit', 'Credit Line Interest', 'USD', 12500.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-28', '2024-12-28', 'SCHEDULED', '', 'HSBC-INT-DEC', 2, 'Interest only'),
            ('PAY-018', 'LOAN-004', 'Riyad Bank', 'LOAN', 'Equipment Finance', 'Vehicle Lease Payment', 'SAR', 89200.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-05', '2025-01-05', 'SCHEDULED', '', 'RYD-VEH-JAN', 2, 'Monthly lease'),

            # OPEX PAYMENTS
            ('PAY-019', 'OPS-001', 'Property Management Co', 'OPEX', 'Rent', 'January 2025 Office Rent', 'SAR', 150000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-01', '2025-01-01', 'SCHEDULED', '', 'RENT-JAN-2025', 1, 'HQ Office'),
            ('PAY-020', 'OPS-002', 'Security Services Co', 'OPEX', 'Security', 'January 2025 Security', 'SAR', 35000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-05', '2025-01-05', 'SCHEDULED', '', 'SEC-JAN-2025', 3, ''),
            ('PAY-021', 'OPS-004', 'Insurance Corporation', 'OPEX', 'Insurance', 'Q1 2025 Property Insurance', 'SAR', 85000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-01', '2025-01-01', 'PENDING', '', 'INS-Q1-2025', 2, 'Quarterly premium'),

            # Additional varied status examples
            ('PAY-022', 'VND-005', 'Microsoft Corporation', 'VENDOR', 'Software', 'Annual License Renewal', 'USD', 45000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-10', '2024-12-10', 'PAID', '2024-12-08', 'MS-365-2025', 2, 'Annual subscription'),
            ('PAY-023', 'HR-004', 'End of Service Provisions', 'HR', 'EOS', 'Employee Resignation EOS', 'SAR', 95000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-05', '2025-01-05', 'PENDING', '', 'EOS-JAN-2025', 2, '5 resignations'),
            ('PAY-024', 'LOAN-005', 'Emirates NBD', 'LOAN', 'Trade Finance', 'LC Settlement', 'AED', 465000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2025-01-10', '2025-01-10', 'PENDING', '', 'ENBD-LC-JAN', 1, 'Trade finance'),
            ('PAY-025', 'STR-004', 'Acquisition Target Delta', 'STRATEGIC', 'M&A', 'Due Diligence Fees', 'EUR', 85000.00, '=IFERROR(H{r}*VLOOKUP(G{r},FX_Rates.$A$6:$B$11,2,0),0)', '2024-12-30', '2024-12-30', 'POSTPONED', '', 'DELTA-DD-2024', 2, 'Delayed to Q1'),
        ]

        for data in payment_data:
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col)
                if isinstance(value, str) and value.startswith('='):
                    cell.value = value.format(r=row)
                else:
                    cell.value = value
                cell.font = self.styles.FONTS['data']
                cell.border = self.styles.BORDERS['thin']

                # Column-specific formatting
                if col in [8, 9]:  # Currency amounts
                    cell.number_format = '#,##0.00'
                    cell.alignment = self.styles.ALIGNMENTS['number']
                elif col in [1, 2, 4, 5, 7, 12, 15]:
                    cell.alignment = self.styles.ALIGNMENTS['center']
                else:
                    cell.alignment = self.styles.ALIGNMENTS['left']

                if row % 2 == 0:
                    cell.fill = self.styles.FILLS['row_alt']

                # Status-based coloring
                if col == 12:
                    status = value
                    if status == 'PAID':
                        cell.fill = self.styles.FILLS['status_paid']
                        cell.font = Font(name='Calibri', size=10, bold=True, color='1B5E20')
                    elif status == 'PENDING':
                        cell.fill = self.styles.FILLS['status_pending']
                        cell.font = Font(name='Calibri', size=10, bold=True, color='E65100')
                    elif status == 'POSTPONED':
                        cell.fill = self.styles.FILLS['status_postponed']
                        cell.font = Font(name='Calibri', size=10, bold=True, color='424242')
                    elif status == 'SCHEDULED':
                        cell.fill = PatternFill(start_color='E3F2FD', end_color='E3F2FD', fill_type='solid')
                        cell.font = Font(name='Calibri', size=10, bold=True, color='1565C0')
                    elif status == 'OVERDUE':
                        cell.fill = self.styles.FILLS['status_overdue']
                        cell.font = Font(name='Calibri', size=10, bold=True, color='B71C1C')

            row += 1

        # Add empty input rows with formulas
        for _ in range(50):
            for col in range(1, 17):
                cell = ws.cell(row=row, column=col)
                cell.border = self.styles.BORDERS['thin']
                cell.fill = self.styles.FILLS['input_cell'] if col != 9 else self.styles.FILLS['row_white']
                if col == 9:  # SAR amount formula
                    cell.value = f'=IFERROR(IF(H{row}="","",H{row}*VLOOKUP(G{row},FX_Rates.$A$6:$B$11,2,0)),0)'
                    cell.number_format = '#,##0.00'
                if col == 3:  # Auto-lookup vendor name
                    cell.value = f'=IFERROR(IF(B{row}="","",VLOOKUP(B{row},Vendor_Master.$A$4:$B$100,2,0)),"")'
            row += 1

        col_widths = [12, 12, 35, 12, 15, 35, 10, 15, 15, 12, 12, 12, 12, 18, 8, 30]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        ws.freeze_panes = 'D6'

        # Add data validation for Status column
        status_validation = DataValidation(
            type="list",
            formula1='"PAID,PENDING,SCHEDULED,POSTPONED,OVERDUE,CANCELLED"',
            allow_blank=True
        )
        status_validation.error = 'Please select a valid status'
        status_validation.errorTitle = 'Invalid Status'
        ws.add_data_validation(status_validation)
        status_validation.add(f'L6:L500')

        # Add data validation for Currency
        ccy_validation = DataValidation(
            type="list",
            formula1='"SAR,USD,AED,EUR,GBP,SGD"',
            allow_blank=True
        )
        ccy_validation.error = 'Please select a valid currency'
        ccy_validation.errorTitle = 'Invalid Currency'
        ws.add_data_validation(ccy_validation)
        ccy_validation.add(f'G6:G500')

        # Add data validation for Priority
        priority_validation = DataValidation(
            type="list",
            formula1='"1,2,3,4,5"',
            allow_blank=True
        )
        priority_validation.error = 'Priority must be 1-5'
        priority_validation.errorTitle = 'Invalid Priority'
        ws.add_data_validation(priority_validation)
        priority_validation.add(f'O6:O500')

        return self

    def build_treasury_calendar_sheet(self):
        """Build main Treasury Calendar with horizontal timeline and vertical categories"""
        ws = self.sheets['Treasury_Calendar']

        # Configuration
        start_date = datetime(2024, 12, 1)  # Calendar start date
        num_days = 60  # Number of days to display
        header_col_start = 4  # First date column (after category labels)

        # =====================================================================
        # ROW 1: Title
        # =====================================================================
        ws.merge_cells('A1:C1')
        ws['A1'] = 'TREASURY CALENDAR'
        ws['A1'].font = self.styles.FONTS['title']
        ws['A1'].fill = self.styles.FILLS['header_primary']
        ws['A1'].alignment = self.styles.ALIGNMENTS['center']
        ws.row_dimensions[1].height = 35

        # =====================================================================
        # ROW 2-7: Date Header Rows (horizontal timeline metadata)
        # =====================================================================
        date_header_rows = {
            2: 'YEAR',
            3: 'MONTH',
            4: 'WEEK #',
            5: 'DAY',
            6: 'DATE',
            7: 'WEEKDAY'
        }

        # Saudi weekday names
        saudi_weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        # Set up date header labels in column A
        for row_num, label in date_header_rows.items():
            ws[f'A{row_num}'] = label
            ws[f'A{row_num}'].font = self.styles.FONTS['header_sub']
            ws[f'A{row_num}'].fill = self.styles.FILLS['total_row']
            ws[f'A{row_num}'].alignment = self.styles.ALIGNMENTS['center']
            ws[f'A{row_num}'].border = self.styles.BORDERS['thin']
            # Merge A-C for labels
            ws.merge_cells(f'A{row_num}:C{row_num}')

        # Populate date columns
        for day_offset in range(num_days):
            current_date = start_date + timedelta(days=day_offset)
            col = header_col_start + day_offset
            col_letter = get_column_letter(col)

            # Year (Row 2)
            cell = ws.cell(row=2, column=col)
            cell.value = current_date.year
            cell.font = self.styles.FONTS['small']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.fill = self.styles.FILLS['header_tertiary']
            cell.border = self.styles.BORDERS['thin']

            # Month (Row 3)
            cell = ws.cell(row=3, column=col)
            cell.value = current_date.strftime('%b')
            cell.font = self.styles.FONTS['header_sub']
            cell.font = Font(name='Calibri', size=10, bold=True, color='FFFFFF')
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.fill = self.styles.FILLS['header_secondary']
            cell.border = self.styles.BORDERS['thin']

            # Week Number (Row 4) - ISO week number
            cell = ws.cell(row=4, column=col)
            cell.value = current_date.isocalendar()[1]
            cell.font = self.styles.FONTS['small']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.fill = self.styles.FILLS['row_alt']
            cell.border = self.styles.BORDERS['thin']

            # Day of month (Row 5)
            cell = ws.cell(row=5, column=col)
            cell.value = current_date.day
            cell.font = self.styles.FONTS['data_bold']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.border = self.styles.BORDERS['thin']

            # Full date (Row 6)
            cell = ws.cell(row=6, column=col)
            cell.value = current_date
            cell.number_format = 'DD-MMM'
            cell.font = self.styles.FONTS['small']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.border = self.styles.BORDERS['thin']

            # Weekday (Row 7)
            cell = ws.cell(row=7, column=col)
            weekday_idx = current_date.weekday()  # 0=Monday, 6=Sunday
            cell.value = saudi_weekdays[weekday_idx]
            cell.font = self.styles.FONTS['small']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.border = self.styles.BORDERS['thin']

            # Weekend highlighting (Friday=4, Saturday=5 in Python weekday)
            if weekday_idx == 4:  # Friday
                for r in range(5, 8):
                    ws.cell(row=r, column=col).fill = self.styles.FILLS['weekend_fri']
            elif weekday_idx == 5:  # Saturday
                for r in range(5, 8):
                    ws.cell(row=r, column=col).fill = self.styles.FILLS['weekend_sat']

            # Column width for dates
            ws.column_dimensions[col_letter].width = 10

        # =====================================================================
        # ROW 8: Separator row
        # =====================================================================
        ws.row_dimensions[8].height = 5
        for col in range(1, header_col_start + num_days):
            cell = ws.cell(row=8, column=col)
            cell.fill = self.styles.FILLS['header_primary']

        # =====================================================================
        # VERTICAL CATEGORIES (Rows 9+)
        # =====================================================================
        categories = [
            # (Category Name, Level, Type, Source Sheet, Date Col, Amount Col)
            ('OPENING BALANCE', 0, 'balance', None, None, None),
            ('Opening Cash Position (SAR)', 1, 'opening', None, None, None),

            ('INFLOWS', 0, 'section', None, None, None),
            ('Expected Collections', 1, 'sumif', 'SRC_Collections', 'H', 'G'),
            ('Deposit Maturities', 1, 'sumif', 'SRC_Deposits', 'I', 'H'),
            ('Other Inflows', 1, 'input', None, None, None),
            ('TOTAL INFLOWS', 1, 'subtotal', None, None, None),

            ('OUTFLOWS', 0, 'section', None, None, None),
            ('Operating Expenditures (OPeX)', 1, 'sumif', 'SRC_OPeX', 'H', 'G'),
            ('Capital Expenditures (CAPEX)', 1, 'sumif', 'SRC_CAPEX', 'H', 'G'),
            ('Human Resources (Payroll)', 1, 'sumif', 'SRC_HR', 'H', 'G'),
            ('Debt Service & Loans', 1, 'sumif', 'SRC_Debt', 'I', 'H'),
            ('Fixed Expenses', 1, 'sumif', 'SRC_Fixed', 'H', 'G'),
            ('Variable Expenses', 1, 'sumif', 'SRC_Variable', 'H', 'G'),
            ('Payment Calendar Items', 1, 'payment', 'Payment_Data', 'J', 'I'),
            ('Other Outflows', 1, 'input', None, None, None),
            ('TOTAL OUTFLOWS', 1, 'subtotal', None, None, None),

            ('NET CASH FLOW', 0, 'net', None, None, None),
            ('Daily Net Position', 1, 'daily_net', None, None, None),

            ('CLOSING BALANCE', 0, 'balance', None, None, None),
            ('Closing Cash Position (SAR)', 1, 'closing', None, None, None),

            ('CUMULATIVE ANALYSIS', 0, 'section', None, None, None),
            ('Cumulative Inflows', 1, 'cumulative_in', None, None, None),
            ('Cumulative Outflows', 1, 'cumulative_out', None, None, None),
            ('Running Balance', 1, 'running', None, None, None),
        ]

        # Track row positions for formula references
        row_map = {}
        current_row = 9

        for cat_name, level, cat_type, source_sheet, date_col, amount_col in categories:
            row_map[cat_name] = current_row

            # Category label in columns A-C
            if level == 0:  # Main section header
                ws.merge_cells(f'A{current_row}:C{current_row}')
                ws[f'A{current_row}'] = cat_name
                ws[f'A{current_row}'].font = self.styles.FONTS['header_main']
                ws[f'A{current_row}'].fill = self.styles.FILLS['header_primary']
                ws[f'A{current_row}'].alignment = self.styles.ALIGNMENTS['left']
                ws[f'A{current_row}'].border = self.styles.BORDERS['header']
                # Fill header across all date columns
                for col in range(header_col_start, header_col_start + num_days):
                    cell = ws.cell(row=current_row, column=col)
                    cell.fill = self.styles.FILLS['header_primary']
                    cell.border = self.styles.BORDERS['thin']
            else:  # Sub-category
                ws.merge_cells(f'A{current_row}:C{current_row}')
                ws[f'A{current_row}'] = f'  {cat_name}'
                ws[f'A{current_row}'].font = self.styles.FONTS['category'] if 'TOTAL' in cat_name else self.styles.FONTS['subcategory']
                ws[f'A{current_row}'].alignment = self.styles.ALIGNMENTS['left']
                ws[f'A{current_row}'].border = self.styles.BORDERS['thin']

                if 'TOTAL' in cat_name or cat_type in ['closing', 'running', 'daily_net']:
                    ws[f'A{current_row}'].fill = self.styles.FILLS['total_row']
                    ws[f'A{current_row}'].font = self.styles.FONTS['total']

            # Populate formulas for each date column
            for day_offset in range(num_days):
                current_date = start_date + timedelta(days=day_offset)
                col = header_col_start + day_offset
                col_letter = get_column_letter(col)
                cell = ws.cell(row=current_row, column=col)

                if level == 0:
                    continue  # Section headers don't have values

                cell.border = self.styles.BORDERS['thin']
                cell.number_format = '#,##0.00'
                cell.alignment = self.styles.ALIGNMENTS['number']

                # Weekend highlighting for data rows
                weekday_idx = current_date.weekday()
                if weekday_idx == 4:  # Friday
                    cell.fill = self.styles.FILLS['weekend_fri']
                elif weekday_idx == 5:  # Saturday
                    cell.fill = self.styles.FILLS['weekend_sat']

                # Formula based on category type
                date_ref = f'{col_letter}$6'  # Reference to the date in row 6

                if cat_type == 'opening':
                    if day_offset == 0:
                        cell.value = 5000000.00  # Initial opening balance
                        cell.fill = self.styles.FILLS['input_cell']
                    else:
                        # Opening = Previous day's closing
                        prev_col = get_column_letter(col - 1)
                        closing_row = row_map.get('Closing Cash Position (SAR)', current_row + 10)
                        cell.value = f'=IFERROR({prev_col}{closing_row},0)'

                elif cat_type == 'sumif':
                    # SUMIF formula to aggregate from source sheet
                    # LibreOffice compatible: SUMIF(range, criteria, sum_range)
                    cell.value = f'=IFERROR(SUMIF({source_sheet}.${date_col}$4:${date_col}$500,{date_ref},{source_sheet}.${amount_col}$4:${amount_col}$500),0)'

                elif cat_type == 'payment':
                    # Sum payments from Payment_Data based on Due Date
                    cell.value = f'=IFERROR(SUMIF(Payment_Data.$J$6:$J$500,{date_ref},Payment_Data.$I$6:$I$500),0)'

                elif cat_type == 'input':
                    cell.value = 0
                    cell.fill = self.styles.FILLS['input_cell']

                elif cat_type == 'subtotal':
                    if 'INFLOWS' in cat_name:
                        # Sum of inflow rows
                        inflow_rows = [
                            row_map.get('Expected Collections'),
                            row_map.get('Deposit Maturities'),
                            row_map.get('Other Inflows'),
                        ]
                        sum_refs = '+'.join([f'{col_letter}{r}' for r in inflow_rows if r])
                        cell.value = f'=IFERROR({sum_refs},0)'
                        cell.fill = self.styles.FILLS['total_row']
                        cell.font = self.styles.FONTS['total']
                    elif 'OUTFLOWS' in cat_name:
                        # Sum of outflow rows
                        outflow_rows = [
                            row_map.get('Operating Expenditures (OPeX)'),
                            row_map.get('Capital Expenditures (CAPEX)'),
                            row_map.get('Human Resources (Payroll)'),
                            row_map.get('Debt Service & Loans'),
                            row_map.get('Fixed Expenses'),
                            row_map.get('Variable Expenses'),
                            row_map.get('Other Outflows'),
                        ]
                        sum_refs = '+'.join([f'{col_letter}{r}' for r in outflow_rows if r])
                        cell.value = f'=IFERROR({sum_refs},0)'
                        cell.fill = self.styles.FILLS['total_row']
                        cell.font = self.styles.FONTS['total']

                elif cat_type == 'daily_net':
                    # Net = Total Inflows - Total Outflows
                    inflow_row = row_map.get('TOTAL INFLOWS')
                    outflow_row = row_map.get('TOTAL OUTFLOWS')
                    cell.value = f'=IFERROR({col_letter}{inflow_row}-{col_letter}{outflow_row},0)'
                    cell.fill = self.styles.FILLS['gold_accent']
                    cell.font = self.styles.FONTS['total']

                elif cat_type == 'closing':
                    # Closing = Opening + Net Cash Flow
                    opening_row = row_map.get('Opening Cash Position (SAR)')
                    net_row = row_map.get('Daily Net Position')
                    cell.value = f'=IFERROR({col_letter}{opening_row}+{col_letter}{net_row},0)'
                    cell.fill = self.styles.FILLS['total_row']
                    cell.font = self.styles.FONTS['total']

                elif cat_type == 'cumulative_in':
                    inflow_row = row_map.get('TOTAL INFLOWS')
                    if day_offset == 0:
                        cell.value = f'=IFERROR({col_letter}{inflow_row},0)'
                    else:
                        prev_col = get_column_letter(col - 1)
                        cell.value = f'=IFERROR({prev_col}{current_row}+{col_letter}{inflow_row},0)'

                elif cat_type == 'cumulative_out':
                    outflow_row = row_map.get('TOTAL OUTFLOWS')
                    if day_offset == 0:
                        cell.value = f'=IFERROR({col_letter}{outflow_row},0)'
                    else:
                        prev_col = get_column_letter(col - 1)
                        cell.value = f'=IFERROR({prev_col}{current_row}+{col_letter}{outflow_row},0)'

                elif cat_type == 'running':
                    closing_row = row_map.get('Closing Cash Position (SAR)')
                    cell.value = f'=IFERROR({col_letter}{closing_row},0)'
                    cell.fill = self.styles.FILLS['gold_accent']
                    cell.font = self.styles.FONTS['total']

            current_row += 1

        # =====================================================================
        # Column widths
        # =====================================================================
        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 5
        ws.column_dimensions['C'].width = 35

        # Freeze panes: Fix rows 1-7 and columns A-C
        ws.freeze_panes = 'D8'

        return self

    def build_payment_calendar_sheet(self):
        """Build Payment Calendar with vendor rows and status-based highlighting"""
        ws = self.sheets['Payment_Calendar']

        # Configuration
        start_date = datetime(2024, 12, 1)  # Calendar start date
        num_days = 60  # Number of days to display
        header_col_start = 5  # First date column (after vendor info columns)

        # =====================================================================
        # ROW 1: Title
        # =====================================================================
        ws.merge_cells('A1:D1')
        ws['A1'] = 'PAYMENT CALENDAR'
        ws['A1'].font = self.styles.FONTS['title']
        ws['A1'].fill = self.styles.FILLS['header_primary']
        ws['A1'].alignment = self.styles.ALIGNMENTS['center']
        ws.row_dimensions[1].height = 35

        # =====================================================================
        # ROW 2: Subtitle with note
        # =====================================================================
        ws.merge_cells('A2:D2')
        ws['A2'] = 'Data sourced from Payment_Data sheet (Single Source of Truth)'
        ws['A2'].font = Font(name='Calibri', size=10, italic=True, color='718096')
        ws['A2'].alignment = self.styles.ALIGNMENTS['center']

        # =====================================================================
        # ROW 3-7: Date Header Rows (same as Treasury Calendar)
        # =====================================================================
        date_header_rows = {
            3: 'YEAR',
            4: 'MONTH',
            5: 'WEEK #',
            6: 'DAY',
            7: 'WEEKDAY'
        }

        saudi_weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        # Column headers A-D
        col_headers = ['Category', 'Vendor/Payee', 'CCY', 'Status']
        for col, header in enumerate(col_headers, 1):
            for row in range(3, 8):
                cell = ws.cell(row=row, column=col)
                if row == 3:
                    cell.value = header
                    cell.font = self.styles.FONTS['header_main']
                    cell.fill = self.styles.FILLS['header_primary']
                else:
                    cell.fill = self.styles.FILLS['header_secondary']
                cell.alignment = self.styles.ALIGNMENTS['center']
                cell.border = self.styles.BORDERS['thin']

        # Populate date columns
        for day_offset in range(num_days):
            current_date = start_date + timedelta(days=day_offset)
            col = header_col_start + day_offset
            col_letter = get_column_letter(col)

            # Year (Row 3)
            cell = ws.cell(row=3, column=col)
            cell.value = current_date.year
            cell.font = self.styles.FONTS['small']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.fill = self.styles.FILLS['header_tertiary']
            cell.border = self.styles.BORDERS['thin']

            # Month (Row 4)
            cell = ws.cell(row=4, column=col)
            cell.value = current_date.strftime('%b')
            cell.font = Font(name='Calibri', size=10, bold=True, color='FFFFFF')
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.fill = self.styles.FILLS['header_secondary']
            cell.border = self.styles.BORDERS['thin']

            # Week Number (Row 5)
            cell = ws.cell(row=5, column=col)
            cell.value = current_date.isocalendar()[1]
            cell.font = self.styles.FONTS['small']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.fill = self.styles.FILLS['row_alt']
            cell.border = self.styles.BORDERS['thin']

            # Day of month (Row 6)
            cell = ws.cell(row=6, column=col)
            cell.value = current_date.day
            cell.font = self.styles.FONTS['data_bold']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.border = self.styles.BORDERS['thin']

            # Weekday (Row 7)
            cell = ws.cell(row=7, column=col)
            weekday_idx = current_date.weekday()
            cell.value = saudi_weekdays[weekday_idx]
            cell.font = self.styles.FONTS['small']
            cell.alignment = self.styles.ALIGNMENTS['center']
            cell.border = self.styles.BORDERS['thin']

            # Weekend highlighting
            if weekday_idx == 4:  # Friday
                for r in range(5, 8):
                    ws.cell(row=r, column=col).fill = self.styles.FILLS['weekend_fri']
            elif weekday_idx == 5:  # Saturday
                for r in range(5, 8):
                    ws.cell(row=r, column=col).fill = self.styles.FILLS['weekend_sat']

            # Column width
            ws.column_dimensions[col_letter].width = 12

        # =====================================================================
        # ROW 8: Separator
        # =====================================================================
        ws.row_dimensions[8].height = 5
        for col in range(1, header_col_start + num_days):
            cell = ws.cell(row=8, column=col)
            cell.fill = self.styles.FILLS['header_primary']

        # =====================================================================
        # Payment Categories and Vendors (Rows 9+)
        # =====================================================================
        # Organized by category with vendors underneath
        payment_structure = [
            # (Type, Level, Category, Vendor ID, Vendor Name, CCY)
            # Level 0 = Category Header, Level 1 = Vendor

            ('HEADER', 0, 'VENDOR PAYMENTS', None, None, None),
            ('VENDOR', 1, 'VENDOR', 'VND-001', 'Saudi Electricity Company', 'SAR'),
            ('VENDOR', 1, 'VENDOR', 'VND-002', 'Saudi Telecom (STC)', 'SAR'),
            ('VENDOR', 1, 'VENDOR', 'VND-004', 'Dell Technologies', 'USD'),
            ('VENDOR', 1, 'VENDOR', 'VND-005', 'Microsoft Corporation', 'USD'),
            ('VENDOR', 1, 'VENDOR', 'VND-006', 'Office Supplies Co', 'SAR'),

            ('HEADER', 0, 'HUMAN RESOURCES', None, None, None),
            ('VENDOR', 1, 'HR', 'HR-001', 'Monthly Payroll', 'SAR'),
            ('VENDOR', 1, 'HR', 'HR-002', 'GOSI (Social Insurance)', 'SAR'),
            ('VENDOR', 1, 'HR', 'HR-003', 'Medical Insurance Provider', 'SAR'),
            ('VENDOR', 1, 'HR', 'HR-004', 'End of Service Provisions', 'SAR'),
            ('VENDOR', 1, 'HR', 'HR-005', 'Staff Bonuses', 'SAR'),

            ('HEADER', 0, 'GOVERNMENT PAYMENTS', None, None, None),
            ('VENDOR', 1, 'GOVT', 'GOV-001', 'ZATCA (Tax Authority)', 'SAR'),
            ('VENDOR', 1, 'GOVT', 'GOV-002', 'Ministry of Labor', 'SAR'),
            ('VENDOR', 1, 'GOVT', 'GOV-003', 'Municipality Fees', 'SAR'),

            ('HEADER', 0, 'STRATEGIC PAYMENTS', None, None, None),
            ('VENDOR', 1, 'STRATEGIC', 'STR-001', 'Strategic Partner Alpha', 'AED'),
            ('VENDOR', 1, 'STRATEGIC', 'STR-002', 'Investment Fund Beta', 'GBP'),
            ('VENDOR', 1, 'STRATEGIC', 'STR-003', 'JV Company Gamma', 'SGD'),
            ('VENDOR', 1, 'STRATEGIC', 'STR-004', 'Acquisition Target Delta', 'EUR'),

            ('HEADER', 0, 'LOAN REPAYMENTS', None, None, None),
            ('VENDOR', 1, 'LOAN', 'LOAN-001', 'Saudi National Bank', 'SAR'),
            ('VENDOR', 1, 'LOAN', 'LOAN-002', 'Al Rajhi Bank', 'SAR'),
            ('VENDOR', 1, 'LOAN', 'LOAN-003', 'HSBC Saudi Arabia', 'USD'),
            ('VENDOR', 1, 'LOAN', 'LOAN-004', 'Riyad Bank', 'SAR'),
            ('VENDOR', 1, 'LOAN', 'LOAN-005', 'Emirates NBD', 'AED'),

            ('HEADER', 0, 'OPERATING EXPENSES', None, None, None),
            ('VENDOR', 1, 'OPEX', 'OPS-001', 'Property Management Co', 'SAR'),
            ('VENDOR', 1, 'OPEX', 'OPS-002', 'Security Services Co', 'SAR'),
            ('VENDOR', 1, 'OPEX', 'OPS-004', 'Insurance Corporation', 'SAR'),

            ('HEADER', 0, 'CATEGORY TOTALS', None, None, None),
            ('TOTAL', 1, 'TOTAL', None, 'Daily Total (SAR)', 'SAR'),
        ]

        current_row = 9

        for ptype, level, category, vendor_id, vendor_name, ccy in payment_structure:

            if level == 0:  # Category Header
                ws.merge_cells(f'A{current_row}:D{current_row}')
                ws[f'A{current_row}'] = category
                ws[f'A{current_row}'].font = self.styles.FONTS['header_main']
                ws[f'A{current_row}'].fill = self.styles.FILLS['header_primary']
                ws[f'A{current_row}'].alignment = self.styles.ALIGNMENTS['left']
                ws[f'A{current_row}'].border = self.styles.BORDERS['header']

                # Fill header across date columns
                for col in range(header_col_start, header_col_start + num_days):
                    cell = ws.cell(row=current_row, column=col)
                    cell.fill = self.styles.FILLS['header_primary']
                    cell.border = self.styles.BORDERS['thin']

            elif ptype == 'TOTAL':
                # Total row
                ws[f'A{current_row}'] = category
                ws[f'A{current_row}'].font = self.styles.FONTS['total']
                ws[f'A{current_row}'].fill = self.styles.FILLS['total_row']
                ws[f'A{current_row}'].border = self.styles.BORDERS['thin']

                ws[f'B{current_row}'] = vendor_name
                ws[f'B{current_row}'].font = self.styles.FONTS['total']
                ws[f'B{current_row}'].fill = self.styles.FILLS['total_row']
                ws[f'B{current_row}'].border = self.styles.BORDERS['thin']

                ws[f'C{current_row}'] = ccy
                ws[f'C{current_row}'].font = self.styles.FONTS['total']
                ws[f'C{current_row}'].fill = self.styles.FILLS['total_row']
                ws[f'C{current_row}'].alignment = self.styles.ALIGNMENTS['center']
                ws[f'C{current_row}'].border = self.styles.BORDERS['thin']

                ws[f'D{current_row}'] = ''
                ws[f'D{current_row}'].fill = self.styles.FILLS['total_row']
                ws[f'D{current_row}'].border = self.styles.BORDERS['thin']

                # Sum formula for each date column
                for day_offset in range(num_days):
                    col = header_col_start + day_offset
                    col_letter = get_column_letter(col)
                    cell = ws.cell(row=current_row, column=col)

                    # Sum all vendor amounts in this column (rows 10 to current_row-1)
                    cell.value = f'=IFERROR(SUM({col_letter}10:{col_letter}{current_row-1}),0)'
                    cell.number_format = '#,##0.00'
                    cell.font = self.styles.FONTS['total']
                    cell.fill = self.styles.FILLS['total_row']
                    cell.border = self.styles.BORDERS['thin']
                    cell.alignment = self.styles.ALIGNMENTS['number']

            else:  # Vendor Row
                # Category column
                ws[f'A{current_row}'] = category
                ws[f'A{current_row}'].font = self.styles.FONTS['small']
                ws[f'A{current_row}'].alignment = self.styles.ALIGNMENTS['center']
                ws[f'A{current_row}'].border = self.styles.BORDERS['thin']

                # Apply category-based coloring
                if category == 'VENDOR':
                    ws[f'A{current_row}'].fill = PatternFill(start_color='E3F2FD', end_color='E3F2FD', fill_type='solid')
                elif category == 'HR':
                    ws[f'A{current_row}'].fill = PatternFill(start_color='E8F5E9', end_color='E8F5E9', fill_type='solid')
                elif category == 'GOVT':
                    ws[f'A{current_row}'].fill = PatternFill(start_color='FFF3E0', end_color='FFF3E0', fill_type='solid')
                elif category == 'STRATEGIC':
                    ws[f'A{current_row}'].fill = PatternFill(start_color='F3E5F5', end_color='F3E5F5', fill_type='solid')
                elif category == 'LOAN':
                    ws[f'A{current_row}'].fill = PatternFill(start_color='FFEBEE', end_color='FFEBEE', fill_type='solid')
                elif category == 'OPEX':
                    ws[f'A{current_row}'].fill = PatternFill(start_color='E0F7FA', end_color='E0F7FA', fill_type='solid')

                # Vendor Name column
                ws[f'B{current_row}'] = vendor_name
                ws[f'B{current_row}'].font = self.styles.FONTS['data']
                ws[f'B{current_row}'].alignment = self.styles.ALIGNMENTS['left']
                ws[f'B{current_row}'].border = self.styles.BORDERS['thin']

                # Currency column
                ws[f'C{current_row}'] = ccy
                ws[f'C{current_row}'].font = self.styles.FONTS['data']
                ws[f'C{current_row}'].alignment = self.styles.ALIGNMENTS['center']
                ws[f'C{current_row}'].border = self.styles.BORDERS['thin']

                # Status column - Formula to get status from Payment_Data
                # Using SUMPRODUCT to find matching payment status
                ws[f'D{current_row}'] = f'=IFERROR(INDEX(Payment_Data.$L$6:$L$100,MATCH("{vendor_id}",Payment_Data.$B$6:$B$100,0)),"")'
                ws[f'D{current_row}'].font = self.styles.FONTS['data']
                ws[f'D{current_row}'].alignment = self.styles.ALIGNMENTS['center']
                ws[f'D{current_row}'].border = self.styles.BORDERS['thin']

                # Date columns with payment amount lookup
                for day_offset in range(num_days):
                    current_date = start_date + timedelta(days=day_offset)
                    col = header_col_start + day_offset
                    col_letter = get_column_letter(col)
                    cell = ws.cell(row=current_row, column=col)
                    date_ref = f'{col_letter}$6'

                    # SUMPRODUCT formula to find payment amount for this vendor on this date
                    # Matches Vendor ID (col B) and Due Date (col J) in Payment_Data
                    # Returns Amount in SAR (col I)
                    cell.value = f'=IFERROR(SUMPRODUCT((Payment_Data.$B$6:$B$100="{vendor_id}")*(Payment_Data.$J$6:$J$100={date_ref})*(Payment_Data.$I$6:$I$100)),0)'
                    cell.number_format = '#,##0.00'
                    cell.border = self.styles.BORDERS['thin']
                    cell.alignment = self.styles.ALIGNMENTS['number']

                    # Weekend highlighting
                    weekday_idx = current_date.weekday()
                    if weekday_idx == 4:  # Friday
                        cell.fill = self.styles.FILLS['weekend_fri']
                    elif weekday_idx == 5:  # Saturday
                        cell.fill = self.styles.FILLS['weekend_sat']

            current_row += 1

        # =====================================================================
        # Add Conditional Formatting for Status-based Highlighting
        # =====================================================================
        # These rules will highlight cells based on whether they have values
        # and the status in column D

        # Add conditional formatting for cells with values > 0
        # Paid = Green, Pending = Orange, Postponed = Gray, Scheduled = Blue

        # Format range for conditional formatting
        data_start_row = 10
        data_end_row = current_row - 2  # Exclude total row
        first_date_col = get_column_letter(header_col_start)
        last_date_col = get_column_letter(header_col_start + num_days - 1)

        # Create conditional formatting rules
        # Rule 1: Highlight cells > 0 in green for PAID status
        paid_rule = FormulaRule(
            formula=[f'AND(${first_date_col}{data_start_row}>0,$D{data_start_row}="PAID")'],
            fill=PatternFill(start_color='C8E6C9', end_color='C8E6C9', fill_type='solid'),
            font=Font(bold=True, color='1B5E20')
        )

        # Rule 2: Highlight cells > 0 in orange for PENDING status
        pending_rule = FormulaRule(
            formula=[f'AND(${first_date_col}{data_start_row}>0,$D{data_start_row}="PENDING")'],
            fill=PatternFill(start_color='FFE0B2', end_color='FFE0B2', fill_type='solid'),
            font=Font(bold=True, color='E65100')
        )

        # Rule 3: Highlight cells > 0 in gray for POSTPONED status
        postponed_rule = FormulaRule(
            formula=[f'AND(${first_date_col}{data_start_row}>0,$D{data_start_row}="POSTPONED")'],
            fill=PatternFill(start_color='E0E0E0', end_color='E0E0E0', fill_type='solid'),
            font=Font(bold=True, color='424242')
        )

        # Rule 4: Highlight cells > 0 in blue for SCHEDULED status
        scheduled_rule = FormulaRule(
            formula=[f'AND(${first_date_col}{data_start_row}>0,$D{data_start_row}="SCHEDULED")'],
            fill=PatternFill(start_color='BBDEFB', end_color='BBDEFB', fill_type='solid'),
            font=Font(bold=True, color='1565C0')
        )

        # Rule 5: Highlight cells > 0 in red for OVERDUE status
        overdue_rule = FormulaRule(
            formula=[f'AND(${first_date_col}{data_start_row}>0,$D{data_start_row}="OVERDUE")'],
            fill=PatternFill(start_color='FFCDD2', end_color='FFCDD2', fill_type='solid'),
            font=Font(bold=True, color='B71C1C')
        )

        # Apply rules to date columns
        format_range = f'{first_date_col}{data_start_row}:{last_date_col}{data_end_row}'
        ws.conditional_formatting.add(format_range, paid_rule)
        ws.conditional_formatting.add(format_range, pending_rule)
        ws.conditional_formatting.add(format_range, postponed_rule)
        ws.conditional_formatting.add(format_range, scheduled_rule)
        ws.conditional_formatting.add(format_range, overdue_rule)

        # Rule 6: General highlight for any cell with value > 0 (fallback)
        value_rule = FormulaRule(
            formula=[f'{first_date_col}{data_start_row}>0'],
            fill=PatternFill(start_color='FFF9C4', end_color='FFF9C4', fill_type='solid'),
            font=Font(bold=True)
        )
        ws.conditional_formatting.add(format_range, value_rule)

        # =====================================================================
        # Column widths
        # =====================================================================
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 30
        ws.column_dimensions['C'].width = 8
        ws.column_dimensions['D'].width = 12

        # Freeze panes
        ws.freeze_panes = 'E8'

        # =====================================================================
        # Add Legend
        # =====================================================================
        legend_row = current_row + 2

        ws[f'A{legend_row}'] = 'STATUS LEGEND:'
        ws[f'A{legend_row}'].font = self.styles.FONTS['category']
        ws.merge_cells(f'A{legend_row}:B{legend_row}')

        legend_items = [
            ('PAID', 'C8E6C9', '1B5E20'),
            ('PENDING', 'FFE0B2', 'E65100'),
            ('SCHEDULED', 'BBDEFB', '1565C0'),
            ('POSTPONED', 'E0E0E0', '424242'),
            ('OVERDUE', 'FFCDD2', 'B71C1C'),
        ]

        legend_row += 1
        for status, bg_color, font_color in legend_items:
            ws[f'A{legend_row}'] = status
            ws[f'A{legend_row}'].fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type='solid')
            ws[f'A{legend_row}'].font = Font(name='Calibri', size=10, bold=True, color=font_color)
            ws[f'A{legend_row}'].alignment = self.styles.ALIGNMENTS['center']
            ws[f'A{legend_row}'].border = self.styles.BORDERS['thin']
            legend_row += 1

        return self

    def save_workbook(self, filename='Treasury_Calendar_Workbook.xlsx'):
        """Save the workbook to file"""
        filepath = f'/home/user/Wedxdev/{filename}'
        self.wb.save(filepath)
        print(f"Workbook saved to: {filepath}")
        return filepath


# ============================================================================
# MAIN EXECUTION - CHUNKS 1 & 2
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("TREASURY CALENDAR WORKBOOK BUILDER - CHUNKS 1 & 2")
    print("Creating base structure, config, and source data sheets...")
    print("=" * 70)

    builder = TreasuryWorkbookBuilder()
    builder.create_all_sheets()

    # CHUNK 1: Config sheets
    print("\nBuilding configuration sheets...")
    builder.build_config_sheet()
    builder.build_fx_rates_sheet()

    # CHUNK 2: Source data sheets
    print("Building source data sheets...")
    builder.build_src_collections_sheet()
    builder.build_src_opex_sheet()
    builder.build_src_capex_sheet()
    builder.build_src_hr_sheet()
    builder.build_src_debt_sheet()
    builder.build_src_fixed_sheet()
    builder.build_src_variable_sheet()
    builder.build_src_deposits_sheet()

    # CHUNK 3: Vendor Master & Payment Data
    print("Building Vendor Master and Payment Data sheets...")
    builder.build_vendor_master_sheet()
    builder.build_payment_data_sheet()

    # CHUNK 4: Treasury Calendar
    print("Building Treasury Calendar main sheet...")
    builder.build_treasury_calendar_sheet()

    # CHUNK 5: Payment Calendar
    print("Building Payment Calendar sheet...")
    builder.build_payment_calendar_sheet()

    filepath = builder.save_workbook()

    print("\nALL CHUNKS COMPLETED:")
    print("  ✓ Base workbook structure created")
    print("  ✓ Config sheet built with all parameters")
    print("  ✓ FX_Rates sheet built with currency matrix")
    print("  ✓ SRC_Collections sheet built")
    print("  ✓ SRC_OPeX sheet built")
    print("  ✓ SRC_CAPEX sheet built")
    print("  ✓ SRC_HR sheet built")
    print("  ✓ SRC_Debt sheet built")
    print("  ✓ SRC_Fixed sheet built")
    print("  ✓ SRC_Variable sheet built")
    print("  ✓ SRC_Deposits sheet built")
    print("  ✓ Vendor_Master sheet built")
    print("  ✓ Payment_Data sheet built (Single Source of Truth)")
    print("  ✓ Treasury_Calendar sheet built with horizontal timeline")
    print("  ✓ Payment_Calendar sheet built with status-based highlighting")
    print(f"\nSheets created: {builder.wb.sheetnames}")
    print("\n" + "=" * 70)
    print("TREASURY CALENDAR WORKBOOK GENERATION COMPLETE!")
    print("=" * 70)
    print(f"\nWorkbook location: {filepath}")
    print("\nKey Features:")
    print("  • Saudi Calendar (Week starts Sunday, Fri/Sat weekend)")
    print("  • Multi-currency support (SAR, USD, AED, EUR, GBP, SGD)")
    print("  • LibreOffice Calc compatible formulas (IFERROR wrapped)")
    print("  • Payment_Data as single source of truth")
    print("  • Status-based conditional formatting")
    print("  • Horizontal timeline with 60-day view")
