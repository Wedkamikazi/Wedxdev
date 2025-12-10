"""
Enterprise Treasury Management System - Excel Workbook Generator
Comprehensive Excel workbook with Wednesday-Only Payment Policy,
Time Deposit tracking, and real-time cash position visibility.
"""

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import (
    Font, Fill, PatternFill, Border, Side, Alignment,
    NamedStyle, Protection, Color
)
from openpyxl.formatting.rule import (
    FormulaRule, ColorScaleRule, CellIsRule, DataBarRule
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.chart import LineChart, BarChart, PieChart, Reference
from openpyxl.formatting import Rule
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.worksheet.table import Table, TableStyleInfo
from datetime import datetime, timedelta
from openpyxl.comments import Comment
import os


class TreasuryWorkbookGenerator:
    """Generator for Enterprise Treasury Management System Excel Workbook"""

    def __init__(self):
        self.wb = Workbook()
        self.setup_styles()

        # Color scheme
        self.colors = {
            'header_bg': 'FF1F4E79',      # Dark blue
            'header_font': 'FFFFFFFF',    # White
            'pending_bg': 'FFFFC000',     # Amber
            'paid_bg': 'FF70AD47',        # Green
            'pst1_bg': 'FFED7D31',        # Orange
            'pst2_bg': 'FFFF0000',        # Red
            'urgent_bg': 'FF7030A0',      # Purple
            'cancelled_bg': 'FFC0C0C0',   # Grey
            'wednesday_bg': 'FFB4C6E7',   # Light blue
            'weekend_bg': 'FFE0E0E0',     # Light grey
            'today_bg': 'FFFFF2CC',       # Light yellow
            'alert_critical': 'FFFF0000',  # Red
            'alert_warning': 'FFFFC000',   # Orange
            'alert_info': 'FFFFF2CC',      # Light yellow
            'alert_success': 'FFC6EFCE',   # Light green
            'tier1_bg': 'FFFF6B6B',        # Light red
            'tier2_bg': 'FFFFD93D',        # Yellow
            'tier3_bg': 'FF6BCB77',        # Light green
        }

    def setup_styles(self):
        """Setup reusable styles"""
        # Header style
        self.header_font = Font(bold=True, color='FFFFFF', size=11)
        self.header_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        self.header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        # Border styles
        self.thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        self.thick_border = Border(
            left=Side(style='medium'),
            right=Side(style='medium'),
            top=Side(style='medium'),
            bottom=Side(style='medium')
        )

        # Currency format
        self.currency_format = '#,##0.00'
        self.date_format = 'YYYY-MM-DD'
        self.percentage_format = '0.00%'

    def apply_header_style(self, cell):
        """Apply header styling to a cell"""
        cell.font = self.header_font
        cell.fill = self.header_fill
        cell.alignment = self.header_alignment
        cell.border = self.thin_border

    def create_named_range(self, name, sheet, cell_range):
        """Create a named range"""
        self.wb.defined_names[name] = f"'{sheet}'!{cell_range}"

    def create_workbook(self, filename='Treasury_Management_System.xlsx'):
        """Create the complete Treasury Management workbook"""
        # Remove default sheet
        if 'Sheet' in self.wb.sheetnames:
            del self.wb['Sheet']

        # Create all sheets in order
        self.create_configuration_sheet()
        self.create_exchange_rate_sheet()
        self.create_master_data_hub()
        self.create_time_deposit_sheet()
        self.create_payment_calendar()
        self.create_treasury_calendar()
        self.create_executive_dashboard()
        self.create_validation_sheet()

        # Save workbook
        output_path = os.path.join(os.path.dirname(__file__), filename)
        self.wb.save(output_path)
        print(f"Treasury Management System workbook created: {output_path}")
        return output_path

    def create_configuration_sheet(self):
        """Create the Configuration sheet with system parameters"""
        ws = self.wb.create_sheet("Configuration", 0)

        # Title
        ws.merge_cells('A1:C1')
        ws['A1'] = 'TREASURY MANAGEMENT SYSTEM - CONFIGURATION'
        ws['A1'].font = Font(bold=True, size=14, color='FFFFFF')
        ws['A1'].fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        ws['A1'].alignment = Alignment(horizontal='center')

        # Headers
        headers = ['Parameter', 'Value', 'Description']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            self.apply_header_style(cell)

        # Configuration parameters
        config_data = [
            ('Base_Currency', 'SAR', 'All final amounts convert to SAR'),
            ('Payment_Day', 4, 'Wednesday (1=Sunday in Saudi week)'),
            ('Weekend_Days', '6,7', 'Friday, Saturday (Saudi weekend)'),
            ('Week_Start', 'Sunday', 'Saudi calendar standard'),
            ('Auto_Postpone_Enabled', 'TRUE', 'System auto-escalates overdue items'),
            ('Volatile_Buffer_Near', 0.02, 'Buffer for Week 1-2 projections (2%)'),
            ('Volatile_Buffer_Far', 0.10, 'Buffer for Week 4+ projections (10%)'),
            ('Reference_Wednesday', datetime.now().strftime('%Y-%m-%d'), 'Base date for Wednesday calculations'),
            ('Surplus_Threshold', 1000000, 'SAR threshold for surplus alert'),
            ('Gap_Threshold', -500000, 'SAR threshold for critical gap alert'),
            ('TD_Default_Rate', 0.05, 'Default Time Deposit rate (5%)'),
            ('Fiscal_Year_Start', '01-01', 'Fiscal year start (MM-DD)'),
        ]

        for row, (param, value, desc) in enumerate(config_data, 4):
            ws.cell(row=row, column=1, value=param).border = self.thin_border
            value_cell = ws.cell(row=row, column=2, value=value)
            value_cell.border = self.thin_border
            if isinstance(value, float) and value < 1:
                value_cell.number_format = self.percentage_format
            elif isinstance(value, (int, float)) and value > 100:
                value_cell.number_format = self.currency_format
            ws.cell(row=row, column=3, value=desc).border = self.thin_border

        # Create named ranges for configuration values
        for row, (param, _, _) in enumerate(config_data, 4):
            ws.cell(row=row, column=1).value = param
            # Named range would be created here in actual Excel

        # Vendor Tier Classification section
        ws.merge_cells('A18:C18')
        ws['A18'] = 'VENDOR TIER CLASSIFICATION'
        ws['A18'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['A18'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        tier_headers = ['Tier', 'Classification', 'Payment Policy']
        for col, header in enumerate(tier_headers, 1):
            cell = ws.cell(row=19, column=col, value=header)
            self.apply_header_style(cell)

        tier_data = [
            (1, 'Critical', 'Government, utilities, payroll, strategic partners - Zero tolerance for delay, Pay BEFORE due date'),
            (2, 'Standard', 'Regular operational vendors - Standard Wednesday payment terms'),
            (3, 'Flexible', 'Vendors with negotiable terms - Maximum float optimization, Pay AFTER due date'),
        ]

        tier_fills = [
            PatternFill(start_color='FF6B6B', end_color='FF6B6B', fill_type='solid'),
            PatternFill(start_color='FFD93D', end_color='FFD93D', fill_type='solid'),
            PatternFill(start_color='6BCB77', end_color='6BCB77', fill_type='solid'),
        ]

        for row_idx, (tier, classification, policy) in enumerate(tier_data, 20):
            tier_cell = ws.cell(row=row_idx, column=1, value=tier)
            tier_cell.fill = tier_fills[tier-1]
            tier_cell.border = self.thin_border
            tier_cell.alignment = Alignment(horizontal='center')

            class_cell = ws.cell(row=row_idx, column=2, value=classification)
            class_cell.fill = tier_fills[tier-1]
            class_cell.border = self.thin_border

            policy_cell = ws.cell(row=row_idx, column=3, value=policy)
            policy_cell.border = self.thin_border
            policy_cell.alignment = Alignment(wrap_text=True)

        # Status codes section
        ws.merge_cells('A25:D25')
        ws['A25'] = 'PAYMENT STATUS CODES'
        ws['A25'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['A25'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        status_headers = ['Status', 'Code', 'Color', 'Description']
        for col, header in enumerate(status_headers, 1):
            cell = ws.cell(row=26, column=col, value=header)
            self.apply_header_style(cell)

        status_data = [
            ('Pending', 'PND', 'Amber', 'Awaiting payment execution'),
            ('Paid', 'PAID', 'Green', 'Successfully executed'),
            ('Postponed-1', 'PST1', 'Orange', 'First automatic postponement'),
            ('Postponed-2+', 'PST2', 'Red', 'Multiple postponements - requires management attention'),
            ('Urgent', 'URG', 'Purple', 'Bypasses Wednesday rule'),
            ('Cancelled', 'CAN', 'Grey', 'Voided payment'),
        ]

        status_fills = {
            'Amber': PatternFill(start_color='FFC000', end_color='FFC000', fill_type='solid'),
            'Green': PatternFill(start_color='70AD47', end_color='70AD47', fill_type='solid'),
            'Orange': PatternFill(start_color='ED7D31', end_color='ED7D31', fill_type='solid'),
            'Red': PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid'),
            'Purple': PatternFill(start_color='7030A0', end_color='7030A0', fill_type='solid'),
            'Grey': PatternFill(start_color='C0C0C0', end_color='C0C0C0', fill_type='solid'),
        }

        for row_idx, (status, code, color, desc) in enumerate(status_data, 27):
            ws.cell(row=row_idx, column=1, value=status).border = self.thin_border
            ws.cell(row=row_idx, column=2, value=code).border = self.thin_border
            color_cell = ws.cell(row=row_idx, column=3, value=color)
            color_cell.fill = status_fills[color]
            color_cell.border = self.thin_border
            ws.cell(row=row_idx, column=4, value=desc).border = self.thin_border

        # Column widths
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 60
        ws.column_dimensions['D'].width = 50

        # Freeze panes
        ws.freeze_panes = 'A4'

    def create_exchange_rate_sheet(self):
        """Create Exchange Rate reference sheet"""
        ws = self.wb.create_sheet("Exchange_Rates")

        # Title
        ws.merge_cells('A1:D1')
        ws['A1'] = 'EXCHANGE RATE TABLE'
        ws['A1'].font = Font(bold=True, size=14, color='FFFFFF')
        ws['A1'].fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        ws['A1'].alignment = Alignment(horizontal='center')

        # Headers
        headers = ['Currency', 'Rate_to_SAR', 'Effective_Date', 'Last_Updated_By']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            self.apply_header_style(cell)

        # Exchange rate data
        rate_data = [
            ('SAR', 1.0000, datetime.now(), 'System'),
            ('USD', 3.7500, datetime.now(), 'System'),
            ('AED', 1.0200, datetime.now(), 'System'),
            ('EUR', 4.0500, datetime.now(), 'System'),
            ('GBP', 4.7200, datetime.now(), 'System'),
            ('SGD', 2.8100, datetime.now(), 'System'),
            ('JPY', 0.0250, datetime.now(), 'System'),
            ('CHF', 4.2000, datetime.now(), 'System'),
        ]

        for row, (currency, rate, date, updated_by) in enumerate(rate_data, 4):
            ws.cell(row=row, column=1, value=currency).border = self.thin_border
            rate_cell = ws.cell(row=row, column=2, value=rate)
            rate_cell.number_format = '0.0000'
            rate_cell.border = self.thin_border
            date_cell = ws.cell(row=row, column=3, value=date)
            date_cell.number_format = self.date_format
            date_cell.border = self.thin_border
            ws.cell(row=row, column=4, value=updated_by).border = self.thin_border

        # Add data validation for currency codes
        dv = DataValidation(type="list", formula1='"SAR,USD,AED,EUR,GBP,SGD,JPY,CHF"', allow_blank=False)
        dv.error = 'Please select a valid currency'
        dv.errorTitle = 'Invalid Currency'
        ws.add_data_validation(dv)

        # Column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 18

        # Add formula helper note
        ws['A13'] = 'CONVERSION FORMULA:'
        ws['A13'].font = Font(bold=True)
        ws['A14'] = '=Amount_Original * VLOOKUP(Currency_Code, Exchange_Rates!A4:B11, 2, FALSE)'
        ws['A14'].font = Font(italic=True, color='666666')

    def create_master_data_hub(self):
        """Create the Master Data Hub - single source of truth"""
        ws = self.wb.create_sheet("Data_Hub")

        # Title
        ws.merge_cells('A1:V1')
        ws['A1'] = 'MASTER DATA HUB - SINGLE SOURCE OF TRUTH'
        ws['A1'].font = Font(bold=True, size=14, color='FFFFFF')
        ws['A1'].fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        ws['A1'].alignment = Alignment(horizontal='center')

        # Column groups with headers
        headers = [
            # Identity group
            ('Payment_ID', 'Unique payment identifier'),
            ('Type_Code', 'AP/TD/OTHER'),
            ('Category', 'OPEX/HR/GOV/STRATEGIC/LOAN'),
            # Counterparty group
            ('Vendor_Name', 'Payee name'),
            ('Vendor_Tier', '1=Critical, 2=Standard, 3=Flexible'),
            ('Contact', 'Vendor contact info'),
            # Dates group
            ('Raw_Due_Date', 'Original obligation date'),
            ('Target_Wednesday', 'Calculated payment date'),
            ('Value_Date', 'Actual payment date'),
            # Amounts group
            ('Amount_Original', 'Amount in original currency'),
            ('Currency_Code', 'SAR/USD/AED/EUR/GBP/SGD'),
            ('FX_Rate', 'Exchange rate applied'),
            ('Amount_SAR', 'Converted to base currency'),
            # Status Engine group
            ('Payment_Status', 'PND/PAID/PST1/PST2/URG/CAN'),
            ('Postpone_Count', 'Number of postponements'),
            ('Last_Action_Date', 'Date of last status change'),
            ('Priority_Flag', 'URGENT/PAYROLL/NORMAL'),
            # Audit group
            ('Created_Date', 'Record creation date'),
            ('Created_By', 'User who created record'),
            ('Modified_Date', 'Last modification date'),
            ('Modified_By', 'User who modified record'),
            ('Notes', 'Additional comments'),
        ]

        # Group headers
        group_config = [
            ('IDENTITY', 'A', 'C', '4472C4'),
            ('COUNTERPARTY', 'D', 'F', '70AD47'),
            ('DATES', 'G', 'I', 'ED7D31'),
            ('AMOUNTS', 'J', 'M', 'FFC000'),
            ('STATUS ENGINE', 'N', 'Q', '7030A0'),
            ('AUDIT', 'R', 'V', '808080'),
        ]

        for group_name, start_col, end_col, color in group_config:
            ws.merge_cells(f'{start_col}2:{end_col}2')
            cell = ws[f'{start_col}2']
            cell.value = group_name
            cell.font = Font(bold=True, color='FFFFFF', size=10)
            cell.fill = PatternFill(start_color=color, end_color=color, fill_type='solid')
            cell.alignment = Alignment(horizontal='center')
            cell.border = self.thick_border

        # Column headers
        for col, (header, tooltip) in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            self.apply_header_style(cell)
            # Add comment for tooltip
            cell.comment = Comment(tooltip, 'Treasury System')

        # Add data validations
        # Type Code validation
        dv_type = DataValidation(type="list", formula1='"AP,TD,OTHER"', allow_blank=False)
        dv_type.error = 'Select: AP, TD, or OTHER'
        ws.add_data_validation(dv_type)
        dv_type.add('B4:B1000')

        # Category validation
        dv_category = DataValidation(type="list", formula1='"OPEX,HR,GOV,STRATEGIC,LOAN,OTHER"', allow_blank=False)
        ws.add_data_validation(dv_category)
        dv_category.add('C4:C1000')

        # Vendor Tier validation
        dv_tier = DataValidation(type="list", formula1='"1,2,3"', allow_blank=False)
        dv_tier.error = 'Select: 1 (Critical), 2 (Standard), or 3 (Flexible)'
        ws.add_data_validation(dv_tier)
        dv_tier.add('E4:E1000')

        # Currency validation
        dv_currency = DataValidation(type="list", formula1='"SAR,USD,AED,EUR,GBP,SGD,CHF,JPY"', allow_blank=False)
        ws.add_data_validation(dv_currency)
        dv_currency.add('K4:K1000')

        # Status validation
        dv_status = DataValidation(type="list", formula1='"PND,PAID,PST1,PST2,URG,CAN"', allow_blank=False)
        ws.add_data_validation(dv_status)
        dv_status.add('N4:N1000')

        # Priority validation
        dv_priority = DataValidation(type="list", formula1='"URGENT,PAYROLL,NORMAL"', allow_blank=False)
        ws.add_data_validation(dv_priority)
        dv_priority.add('Q4:Q1000')

        # Sample data entries
        sample_data = [
            ('PAY-2024-001', 'AP', 'OPEX', 'Vendor Alpha Co.', 1, 'contact@alpha.com',
             datetime(2024, 12, 15), None, None, 50000, 'USD', 3.75, None,
             'PND', 0, None, 'NORMAL', datetime.now(), 'Admin', None, None, 'Regular vendor payment'),
            ('PAY-2024-002', 'AP', 'GOV', 'GOSI Payment', 1, 'gov@gosi.sa',
             datetime(2024, 12, 10), None, None, 125000, 'SAR', 1.00, None,
             'PND', 0, None, 'URGENT', datetime.now(), 'Admin', None, None, 'Government obligation'),
            ('PAY-2024-003', 'AP', 'HR', 'Monthly Payroll', 1, 'hr@company.com',
             datetime(2024, 12, 25), None, None, 2500000, 'SAR', 1.00, None,
             'PND', 0, None, 'PAYROLL', datetime.now(), 'Admin', None, None, 'December payroll'),
            ('PAY-2024-004', 'AP', 'OPEX', 'Supplier Beta Ltd', 2, 'pay@beta.com',
             datetime(2024, 12, 18), None, None, 75000, 'EUR', 4.05, None,
             'PND', 0, None, 'NORMAL', datetime.now(), 'Admin', None, None, 'Quarterly supplies'),
            ('PAY-2024-005', 'AP', 'LOAN', 'Bank Loan Principal', 1, 'loans@bank.com',
             datetime(2024, 12, 31), None, None, 500000, 'SAR', 1.00, None,
             'PND', 0, None, 'NORMAL', datetime.now(), 'Admin', None, None, 'Loan installment'),
            ('PAY-2024-006', 'AP', 'OPEX', 'Flexible Supplier X', 3, 'accounts@supplierx.com',
             datetime(2024, 12, 20), None, None, 30000, 'AED', 1.02, None,
             'PND', 0, None, 'NORMAL', datetime.now(), 'Admin', None, None, 'Negotiable terms'),
        ]

        for row_idx, data in enumerate(sample_data, 4):
            for col_idx, value in enumerate(data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = self.thin_border

                # Format specific columns
                if col_idx in [7, 8, 9, 16, 18, 20]:  # Date columns
                    if value:
                        cell.number_format = self.date_format
                elif col_idx in [10, 13]:  # Amount columns
                    if value:
                        cell.number_format = self.currency_format
                elif col_idx == 12:  # FX Rate
                    if value:
                        cell.number_format = '0.0000'

        # Add formulas for calculated columns
        for row in range(4, 10):
            # Target_Wednesday formula (H column) - Wednesday Snap Logic
            ws.cell(row=row, column=8).value = (
                f'=IF(OR($Q{row}="URGENT",$Q{row}="PAYROLL"),'
                f'$G{row},'  # Keep original date for URGENT/PAYROLL
                f'IF($E{row}=1,'  # Tier 1 - Critical
                f'$G{row}-MOD($G{row}-DATE(2024,12,11),7),'  # Previous Wednesday
                f'$G{row}+MOD(DATE(2024,12,11)-$G{row}+7,7)))'  # Next Wednesday for Tier 2-3
            )
            ws.cell(row=row, column=8).number_format = self.date_format

            # Amount_SAR formula (M column)
            ws.cell(row=row, column=13).value = f'=$J{row}*$L{row}'
            ws.cell(row=row, column=13).number_format = self.currency_format

        # Conditional formatting for status
        # Pending - Amber
        ws.conditional_formatting.add('N4:N1000',
            CellIsRule(operator='equal', formula=['"PND"'],
                      fill=PatternFill(start_color='FFC000', end_color='FFC000', fill_type='solid')))
        # Paid - Green
        ws.conditional_formatting.add('N4:N1000',
            CellIsRule(operator='equal', formula=['"PAID"'],
                      fill=PatternFill(start_color='70AD47', end_color='70AD47', fill_type='solid')))
        # PST1 - Orange
        ws.conditional_formatting.add('N4:N1000',
            CellIsRule(operator='equal', formula=['"PST1"'],
                      fill=PatternFill(start_color='ED7D31', end_color='ED7D31', fill_type='solid')))
        # PST2 - Red
        ws.conditional_formatting.add('N4:N1000',
            CellIsRule(operator='equal', formula=['"PST2"'],
                      fill=PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid'),
                      font=Font(color='FFFFFF', bold=True)))
        # URG - Purple
        ws.conditional_formatting.add('N4:N1000',
            CellIsRule(operator='equal', formula=['"URG"'],
                      fill=PatternFill(start_color='7030A0', end_color='7030A0', fill_type='solid'),
                      font=Font(color='FFFFFF')))
        # CAN - Grey
        ws.conditional_formatting.add('N4:N1000',
            CellIsRule(operator='equal', formula=['"CAN"'],
                      fill=PatternFill(start_color='C0C0C0', end_color='C0C0C0', fill_type='solid')))

        # Column widths
        col_widths = [15, 10, 12, 25, 10, 25, 12, 15, 12, 15, 10, 10, 15, 12, 12, 15, 12, 12, 12, 12, 12, 30]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        # Freeze panes
        ws.freeze_panes = 'D4'

    def create_time_deposit_sheet(self):
        """Create Time Deposit Tracking Module"""
        ws = self.wb.create_sheet("Time_Deposits")

        # Title
        ws.merge_cells('A1:O1')
        ws['A1'] = 'TIME DEPOSIT TRACKING MODULE'
        ws['A1'].font = Font(bold=True, size=14, color='FFFFFF')
        ws['A1'].fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        ws['A1'].alignment = Alignment(horizontal='center')

        # TD Master Data headers
        td_headers = [
            'TD_ID', 'Bank', 'Account_No', 'Currency', 'Start_Date', 'Maturity_Date',
            'Principal_Original', 'Rate_Percent', 'Days', 'Profit_Original',
            'Maturity_Amount', 'Status', 'Week_ID', 'Principal_SAR', 'Profit_SAR'
        ]

        for col, header in enumerate(td_headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            self.apply_header_style(cell)

        # Sample TD data
        td_sample_data = [
            ('TD-2024-001', 'Al Rajhi Bank', 'SA1234567890', 'SAR', datetime(2024, 11, 1), datetime(2024, 12, 15),
             5000000, 0.055, None, None, None, None, None, None, None),
            ('TD-2024-002', 'Saudi National Bank', 'SA0987654321', 'SAR', datetime(2024, 11, 15), datetime(2024, 12, 20),
             3000000, 0.052, None, None, None, None, None, None, None),
            ('TD-2024-003', 'SABB', 'SA1122334455', 'USD', datetime(2024, 10, 1), datetime(2024, 12, 31),
             1000000, 0.048, None, None, None, None, None, None, None),
            ('TD-2024-004', 'Riyad Bank', 'SA5544332211', 'SAR', datetime(2024, 12, 1), datetime(2025, 1, 15),
             2000000, 0.05, None, None, None, None, None, None, None),
            ('TD-2024-005', 'Al Rajhi Bank', 'SA9988776655', 'SAR', datetime(2024, 12, 5), datetime(2025, 2, 5),
             4000000, 0.053, None, None, None, None, None, None, None),
        ]

        for row_idx, data in enumerate(td_sample_data, 4):
            for col_idx, value in enumerate(data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = self.thin_border

        # Add formulas for each TD row
        for row in range(4, 9):
            # Days formula (I column)
            ws.cell(row=row, column=9).value = f'=$F{row}-$E{row}'

            # Profit formula (J column) - Principal × Rate × Days/365
            ws.cell(row=row, column=10).value = f'=$G{row}*$H{row}*$I{row}/365'
            ws.cell(row=row, column=10).number_format = self.currency_format

            # Maturity Amount formula (K column)
            ws.cell(row=row, column=11).value = f'=$G{row}+$J{row}'
            ws.cell(row=row, column=11).number_format = self.currency_format

            # Status formula (L column)
            ws.cell(row=row, column=12).value = (
                f'=IF($F{row}<TODAY(),"CLOSED",'
                f'IF($F{row}=TODAY(),"ACTION REQUIRED","ACTIVE"))'
            )

            # Week_ID formula (M column) - Saudi week number (Sunday start)
            ws.cell(row=row, column=13).value = f'=WEEKNUM($F{row},2)'

            # Principal_SAR formula (N column)
            ws.cell(row=row, column=14).value = (
                f'=IF($D{row}="SAR",$G{row},'
                f'$G{row}*VLOOKUP($D{row},Exchange_Rates!$A$4:$B$11,2,FALSE))'
            )
            ws.cell(row=row, column=14).number_format = self.currency_format

            # Profit_SAR formula (O column)
            ws.cell(row=row, column=15).value = (
                f'=IF($D{row}="SAR",$J{row},'
                f'$J{row}*VLOOKUP($D{row},Exchange_Rates!$A$4:$B$11,2,FALSE))'
            )
            ws.cell(row=row, column=15).number_format = self.currency_format

        # Conditional formatting for status
        ws.conditional_formatting.add('L4:L100',
            CellIsRule(operator='equal', formula=['"ACTIVE"'],
                      fill=PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid'),
                      font=Font(color='006100')))
        ws.conditional_formatting.add('L4:L100',
            CellIsRule(operator='equal', formula=['"ACTION REQUIRED"'],
                      fill=PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid'),
                      font=Font(color='9C5700', bold=True)))
        ws.conditional_formatting.add('L4:L100',
            CellIsRule(operator='equal', formula=['"CLOSED"'],
                      fill=PatternFill(start_color='C0C0C0', end_color='C0C0C0', fill_type='solid')))

        # Analytics Section - Maturity Ladder
        ws.merge_cells('A12:F12')
        ws['A12'] = 'MATURITY LADDER (LIQUIDITY PLANNING)'
        ws['A12'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['A12'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        ladder_headers = ['Period', 'Principal Maturing (SAR)', 'Interest Earned (SAR)', 'Total Available', 'Count', 'Cumulative']
        for col, header in enumerate(ladder_headers, 1):
            cell = ws.cell(row=13, column=col, value=header)
            self.apply_header_style(cell)

        ladder_periods = [
            ('This Week', '=SUMIFS($N$4:$N$100,$M$4:$M$100,WEEKNUM(TODAY(),2))'),
            ('Week +1', '=SUMIFS($N$4:$N$100,$M$4:$M$100,WEEKNUM(TODAY(),2)+1)'),
            ('Week +2', '=SUMIFS($N$4:$N$100,$M$4:$M$100,WEEKNUM(TODAY(),2)+2)'),
            ('Week +3', '=SUMIFS($N$4:$N$100,$M$4:$M$100,WEEKNUM(TODAY(),2)+3)'),
            ('Month +1', '=SUMIFS($N$4:$N$100,$F$4:$F$100,">="&DATE(YEAR(TODAY()),MONTH(TODAY())+1,1),$F$4:$F$100,"<"&DATE(YEAR(TODAY()),MONTH(TODAY())+2,1))'),
        ]

        for row_idx, (period, principal_formula) in enumerate(ladder_periods, 14):
            ws.cell(row=row_idx, column=1, value=period).border = self.thin_border
            ws.cell(row=row_idx, column=2, value=principal_formula).border = self.thin_border
            ws.cell(row=row_idx, column=2).number_format = self.currency_format
            # Interest earned formula
            ws.cell(row=row_idx, column=3, value=principal_formula.replace('$N$', '$O$')).border = self.thin_border
            ws.cell(row=row_idx, column=3).number_format = self.currency_format
            # Total available
            ws.cell(row=row_idx, column=4, value=f'=$B{row_idx}+$C{row_idx}').border = self.thin_border
            ws.cell(row=row_idx, column=4).number_format = self.currency_format

        # Bank Concentration Analysis
        ws.merge_cells('A21:E21')
        ws['A21'] = 'BANK CONCENTRATION ANALYSIS'
        ws['A21'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['A21'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        bank_headers = ['Bank', 'Active TDs', 'Total Principal (SAR)', '% of Portfolio', 'Avg Rate']
        for col, header in enumerate(bank_headers, 1):
            cell = ws.cell(row=22, column=col, value=header)
            self.apply_header_style(cell)

        banks = ['Al Rajhi Bank', 'Saudi National Bank', 'SABB', 'Riyad Bank']
        for row_idx, bank in enumerate(banks, 23):
            ws.cell(row=row_idx, column=1, value=bank).border = self.thin_border
            # Active TDs count
            ws.cell(row=row_idx, column=2, value=f'=COUNTIFS($B$4:$B$100,"{bank}",$L$4:$L$100,"ACTIVE")').border = self.thin_border
            # Total Principal
            ws.cell(row=row_idx, column=3, value=f'=SUMIFS($N$4:$N$100,$B$4:$B$100,"{bank}",$L$4:$L$100,"ACTIVE")').border = self.thin_border
            ws.cell(row=row_idx, column=3).number_format = self.currency_format
            # Percentage
            ws.cell(row=row_idx, column=4, value=f'=IFERROR($C{row_idx}/SUM($C$23:$C$26),0)').border = self.thin_border
            ws.cell(row=row_idx, column=4).number_format = self.percentage_format
            # Average Rate
            ws.cell(row=row_idx, column=5, value=f'=IFERROR(AVERAGEIFS($H$4:$H$100,$B$4:$B$100,"{bank}",$L$4:$L$100,"ACTIVE"),0)').border = self.thin_border
            ws.cell(row=row_idx, column=5).number_format = self.percentage_format

        # Currency Breakdown
        ws.merge_cells('G21:K21')
        ws['G21'] = 'CURRENCY BREAKDOWN'
        ws['G21'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['G21'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        curr_headers = ['Currency', 'Principal (Original)', 'Principal (SAR)', 'Count', '% of Total']
        for col, header in enumerate(curr_headers, 7):
            cell = ws.cell(row=22, column=col, value=header)
            self.apply_header_style(cell)

        currencies = ['SAR', 'USD', 'EUR', 'GBP']
        for row_idx, currency in enumerate(currencies, 23):
            ws.cell(row=row_idx, column=7, value=currency).border = self.thin_border
            # Original Principal
            ws.cell(row=row_idx, column=8, value=f'=SUMIFS($G$4:$G$100,$D$4:$D$100,"{currency}",$L$4:$L$100,"ACTIVE")').border = self.thin_border
            ws.cell(row=row_idx, column=8).number_format = self.currency_format
            # SAR Principal
            ws.cell(row=row_idx, column=9, value=f'=SUMIFS($N$4:$N$100,$D$4:$D$100,"{currency}",$L$4:$L$100,"ACTIVE")').border = self.thin_border
            ws.cell(row=row_idx, column=9).number_format = self.currency_format
            # Count
            ws.cell(row=row_idx, column=10, value=f'=COUNTIFS($D$4:$D$100,"{currency}",$L$4:$L$100,"ACTIVE")').border = self.thin_border
            # Percentage
            ws.cell(row=row_idx, column=11, value=f'=IFERROR($I{row_idx}/SUM($I$23:$I$26),0)').border = self.thin_border
            ws.cell(row=row_idx, column=11).number_format = self.percentage_format

        # Column widths
        col_widths = [14, 20, 18, 10, 12, 14, 18, 12, 8, 16, 16, 16, 10, 16, 14]
        for col, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(col)].width = width

        # Freeze panes
        ws.freeze_panes = 'A4'

    def create_payment_calendar(self):
        """Create Payment Calendar with rolling date timeline"""
        ws = self.wb.create_sheet("Payment_Calendar")

        # Title
        ws.merge_cells('A1:AE1')
        ws['A1'] = 'PAYMENT CALENDAR - WEDNESDAY PAYMENT SCHEDULE'
        ws['A1'].font = Font(bold=True, size=14, color='FFFFFF')
        ws['A1'].fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        ws['A1'].alignment = Alignment(horizontal='center')

        # Generate date columns for next 30 days
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday() + 1)  # Start from last Sunday

        # Fixed columns
        fixed_headers = ['Category', 'Vendor', 'Status', 'Amount_SAR']
        for col, header in enumerate(fixed_headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            self.apply_header_style(cell)

        # Date columns
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            col = 5 + day
            cell = ws.cell(row=3, column=col, value=current_date)
            cell.number_format = 'DD-MMM'
            cell.font = Font(bold=True, size=9)
            cell.alignment = Alignment(horizontal='center', text_rotation=45)
            cell.border = self.thin_border

            # Highlight Wednesdays
            if current_date.weekday() == 2:  # Wednesday
                cell.fill = PatternFill(start_color='B4C6E7', end_color='B4C6E7', fill_type='solid')
                cell.font = Font(bold=True, size=9, color='1F4E79')
            # Grey out weekends (Friday=4, Saturday=5 in Python)
            elif current_date.weekday() in [4, 5]:
                cell.fill = PatternFill(start_color='E0E0E0', end_color='E0E0E0', fill_type='solid')
                cell.font = Font(size=9, color='808080')
            # Highlight today
            if current_date.date() == today.date():
                cell.fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
                cell.font = Font(bold=True, size=9)

        # Category structure with sample data
        categories = [
            ('OPERATING EXPENSES (OPEX)', [
                ('Vendor Alpha Co.', 'PND', 187500),
                ('Supplier Beta Ltd', 'PND', 303750),
                ('Flexible Supplier X', 'PND', 30600),
            ]),
            ('HUMAN RESOURCES', [
                ('Monthly Payroll', 'PND', 2500000),
                ('End of Service', 'PND', 0),
                ('Benefits & Allowances', 'PND', 0),
            ]),
            ('GOVERNMENT OBLIGATIONS', [
                ('VAT Payment', 'PND', 0),
                ('GOSI Payment', 'URG', 125000),
                ('Zakat', 'PND', 0),
            ]),
            ('STRATEGIC PAYMENTS', [
                ('Partner X', 'PND', 0),
                ('Partner Y', 'PND', 0),
            ]),
            ('LOAN SERVICING', [
                ('Bank Loan Principal', 'PND', 500000),
                ('Bank Loan Interest', 'PND', 0),
            ]),
        ]

        row = 4
        for category, vendors in categories:
            # Category header
            ws.merge_cells(f'A{row}:D{row}')
            cat_cell = ws.cell(row=row, column=1, value=category)
            cat_cell.font = Font(bold=True, color='FFFFFF')
            cat_cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cat_cell.border = self.thick_border
            row += 1

            for vendor, status, amount in vendors:
                ws.cell(row=row, column=1, value='').border = self.thin_border
                ws.cell(row=row, column=2, value=vendor).border = self.thin_border

                status_cell = ws.cell(row=row, column=3, value=status)
                status_cell.border = self.thin_border
                status_cell.alignment = Alignment(horizontal='center')

                amount_cell = ws.cell(row=row, column=4, value=amount)
                amount_cell.number_format = self.currency_format
                amount_cell.border = self.thin_border

                # Add date cells with formulas
                for day in range(30):
                    col = 5 + day
                    cell = ws.cell(row=row, column=col)
                    cell.border = self.thin_border
                    cell.alignment = Alignment(horizontal='right')
                    cell.number_format = self.currency_format

                    # Conditional placeholder - actual formula would reference Data_Hub
                    current_date = start_date + timedelta(days=day)
                    if current_date.weekday() in [4, 5]:  # Weekend
                        cell.fill = PatternFill(start_color='E0E0E0', end_color='E0E0E0', fill_type='solid')
                    elif current_date.weekday() == 2:  # Wednesday
                        cell.fill = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')

                row += 1

        # Summary row
        row += 1
        ws.merge_cells(f'A{row}:C{row}')
        total_cell = ws.cell(row=row, column=1, value='TOTAL PAYMENTS')
        total_cell.font = Font(bold=True)
        total_cell.fill = PatternFill(start_color='FFC000', end_color='FFC000', fill_type='solid')
        total_cell.border = self.thick_border

        # Total amount
        ws.cell(row=row, column=4, value=f'=SUM(D5:D{row-1})').border = self.thick_border
        ws.cell(row=row, column=4).number_format = self.currency_format
        ws.cell(row=row, column=4).font = Font(bold=True)

        # Column totals for each date
        for day in range(30):
            col = 5 + day
            cell = ws.cell(row=row, column=col)
            cell.value = f'=SUM({get_column_letter(col)}5:{get_column_letter(col)}{row-1})'
            cell.number_format = self.currency_format
            cell.font = Font(bold=True)
            cell.border = self.thick_border

            current_date = start_date + timedelta(days=day)
            if current_date.weekday() == 2:  # Wednesday
                cell.fill = PatternFill(start_color='B4C6E7', end_color='B4C6E7', fill_type='solid')

        # Column widths
        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 22
        ws.column_dimensions['C'].width = 10
        ws.column_dimensions['D'].width = 15
        for col in range(5, 35):
            ws.column_dimensions[get_column_letter(col)].width = 10

        # Freeze panes
        ws.freeze_panes = 'E4'

    def create_treasury_calendar(self):
        """Create Treasury Calendar with cash position view"""
        ws = self.wb.create_sheet("Treasury_Calendar")

        # Title
        ws.merge_cells('A1:I1')
        ws['A1'] = 'TREASURY CALENDAR - CASH POSITION VIEW'
        ws['A1'].font = Font(bold=True, size=14, color='FFFFFF')
        ws['A1'].fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        ws['A1'].alignment = Alignment(horizontal='center')

        # Generate Wednesday columns
        today = datetime.now()
        # Find next Wednesday
        days_until_wednesday = (2 - today.weekday()) % 7
        if days_until_wednesday == 0:
            next_wednesday = today
        else:
            next_wednesday = today + timedelta(days=days_until_wednesday)

        wednesdays = [next_wednesday + timedelta(weeks=i) for i in range(8)]

        # Headers
        headers = ['Metric']
        for wed in wednesdays:
            headers.append(wed.strftime('%d-%b'))

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col, value=header)
            self.apply_header_style(cell)
            if col > 1:
                cell.fill = PatternFill(start_color='B4C6E7', end_color='B4C6E7', fill_type='solid')
                cell.font = Font(bold=True, color='1F4E79')

        # Demand Stream (Outflows)
        ws.merge_cells('A4:I4')
        ws['A4'] = 'DEMAND STREAM (OUTFLOWS)'
        ws['A4'].font = Font(bold=True, color='FFFFFF')
        ws['A4'].fill = PatternFill(start_color='C00000', end_color='C00000', fill_type='solid')

        demand_metrics = [
            ('Confirmed AP (Tier 1-2)', [875000, 650000, 420000, 380000, 290000, 350000, 400000, 320000]),
            ('Estimated AP (Recurring)', [150000, 150000, 150000, 150000, 150000, 150000, 150000, 150000]),
            ('Payroll', [0, 0, 0, 2500000, 0, 0, 0, 0]),
            ('Government Obligations', [125000, 0, 0, 0, 0, 0, 0, 0]),
            ('Loan Servicing', [0, 0, 0, 500000, 0, 0, 0, 0]),
        ]

        row = 5
        for metric, values in demand_metrics:
            ws.cell(row=row, column=1, value=metric).border = self.thin_border
            for col, value in enumerate(values, 2):
                cell = ws.cell(row=row, column=col, value=value)
                cell.number_format = self.currency_format
                cell.border = self.thin_border
            row += 1

        # Volatile Buffer row
        ws.cell(row=row, column=1, value='Volatile Buffer').border = self.thin_border
        for col in range(2, 10):
            # 2% for weeks 1-2, 10% for weeks 3+
            buffer_pct = 0.02 if col <= 3 else 0.10
            cell = ws.cell(row=row, column=col)
            cell.value = f'=SUM({get_column_letter(col)}5:{get_column_letter(col)}9)*{buffer_pct}'
            cell.number_format = self.currency_format
            cell.border = self.thin_border
            cell.fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
        row += 1

        # Total Required row
        ws.cell(row=row, column=1, value='TOTAL CASH REQUIRED').border = self.thick_border
        ws.cell(row=row, column=1).font = Font(bold=True)
        ws.cell(row=row, column=1).fill = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')
        for col in range(2, 10):
            cell = ws.cell(row=row, column=col)
            cell.value = f'=SUM({get_column_letter(col)}5:{get_column_letter(col)}{row-1})'
            cell.number_format = self.currency_format
            cell.border = self.thick_border
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')
        required_row = row
        row += 2

        # Supply Stream (Inflows)
        ws.merge_cells(f'A{row}:I{row}')
        ws[f'A{row}'] = 'SUPPLY STREAM (INFLOWS)'
        ws[f'A{row}'].font = Font(bold=True, color='FFFFFF')
        ws[f'A{row}'].fill = PatternFill(start_color='00B050', end_color='00B050', fill_type='solid')
        row += 1

        supply_metrics = [
            ('Maturing TD Principal', [5000000, 3000000, 0, 0, 2000000, 4000000, 0, 0]),
            ('Maturing TD Interest', [45000, 27000, 0, 0, 15000, 35000, 0, 0]),
            ('Operating Cash', [500000, 500000, 500000, 500000, 500000, 500000, 500000, 500000]),
            ('AR Collections', [350000, 400000, 380000, 420000, 390000, 410000, 400000, 380000]),
        ]

        supply_start = row
        for metric, values in supply_metrics:
            ws.cell(row=row, column=1, value=metric).border = self.thin_border
            for col, value in enumerate(values, 2):
                cell = ws.cell(row=row, column=col, value=value)
                cell.number_format = self.currency_format
                cell.border = self.thin_border
            row += 1

        # Total Available row
        ws.cell(row=row, column=1, value='TOTAL CASH AVAILABLE').border = self.thick_border
        ws.cell(row=row, column=1).font = Font(bold=True)
        ws.cell(row=row, column=1).fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
        for col in range(2, 10):
            cell = ws.cell(row=row, column=col)
            cell.value = f'=SUM({get_column_letter(col)}{supply_start}:{get_column_letter(col)}{row-1})'
            cell.number_format = self.currency_format
            cell.border = self.thick_border
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
        available_row = row
        row += 2

        # Delta Engine
        ws.merge_cells(f'A{row}:I{row}')
        ws[f'A{row}'] = 'DELTA ENGINE'
        ws[f'A{row}'].font = Font(bold=True, color='FFFFFF')
        ws[f'A{row}'].fill = PatternFill(start_color='7030A0', end_color='7030A0', fill_type='solid')
        row += 1

        # Net Position row
        ws.cell(row=row, column=1, value='NET POSITION (Delta)').border = self.thick_border
        ws.cell(row=row, column=1).font = Font(bold=True)
        for col in range(2, 10):
            cell = ws.cell(row=row, column=col)
            cell.value = f'={get_column_letter(col)}{available_row}-{get_column_letter(col)}{required_row}'
            cell.number_format = self.currency_format
            cell.border = self.thick_border
            cell.font = Font(bold=True)
        delta_row = row
        row += 1

        # Action Flag row
        ws.cell(row=row, column=1, value='ACTION FLAG').border = self.thick_border
        ws.cell(row=row, column=1).font = Font(bold=True)
        for col in range(2, 10):
            cell = ws.cell(row=row, column=col)
            cell.value = (
                f'=IF({get_column_letter(col)}{delta_row}>1000000,"SURPLUS - Roll to TD",'
                f'IF({get_column_letter(col)}{delta_row}<-500000,"GAP - Book TD or Draw OD","BALANCED"))'
            )
            cell.border = self.thick_border
            cell.alignment = Alignment(horizontal='center', wrap_text=True)
        row += 2

        # Conditional formatting for delta
        ws.conditional_formatting.add(f'B{delta_row}:I{delta_row}',
            CellIsRule(operator='greaterThan', formula=['1000000'],
                      fill=PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid'),
                      font=Font(color='006100', bold=True)))
        ws.conditional_formatting.add(f'B{delta_row}:I{delta_row}',
            CellIsRule(operator='lessThan', formula=['-500000'],
                      fill=PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid'),
                      font=Font(color='9C0006', bold=True)))

        # Column widths
        ws.column_dimensions['A'].width = 25
        for col in range(2, 10):
            ws.column_dimensions[get_column_letter(col)].width = 15

        # Freeze panes
        ws.freeze_panes = 'B4'

    def create_executive_dashboard(self):
        """Create Executive Dashboard with key metrics and alerts"""
        ws = self.wb.create_sheet("Dashboard")

        # Title
        ws.merge_cells('A1:H1')
        ws['A1'] = 'EXECUTIVE TREASURY DASHBOARD'
        ws['A1'].font = Font(bold=True, size=16, color='FFFFFF')
        ws['A1'].fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        ws['A1'].alignment = Alignment(horizontal='center')

        # Date display
        ws['A2'] = f'As of: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        ws['A2'].font = Font(italic=True, size=10)

        # Key Metrics Panel
        ws.merge_cells('A4:D4')
        ws['A4'] = 'KEY METRICS'
        ws['A4'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['A4'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        metrics = [
            ('Total Payments Due This Week', '=SUMIFS(Data_Hub!$M$4:$M$100,Data_Hub!$H$4:$H$100,">="&TODAY(),Data_Hub!$H$4:$H$100,"<"&TODAY()+7,Data_Hub!$N$4:$N$100,"<>"&"PAID")', 'SAR'),
            ('Total TDs Maturing Today', '=SUMIFS(Time_Deposits!$N$4:$N$100,Time_Deposits!$F$4:$F$100,TODAY())', 'SAR'),
            ('Net Cash Position (This Week)', '=Treasury_Calendar!B18-Treasury_Calendar!B11', 'SAR'),
            ('Overdue Payments Count', '=COUNTIFS(Data_Hub!$N$4:$N$100,"PST*")', 'Count'),
            ('Urgent Items', '=COUNTIFS(Data_Hub!$N$4:$N$100,"URG")', 'Count'),
            ('Active Time Deposits', '=COUNTIFS(Time_Deposits!$L$4:$L$100,"ACTIVE")', 'Count'),
            ('Total TD Principal (Active)', '=SUMIFS(Time_Deposits!$N$4:$N$100,Time_Deposits!$L$4:$L$100,"ACTIVE")', 'SAR'),
        ]

        for row, (metric, formula, unit) in enumerate(metrics, 5):
            ws.cell(row=row, column=1, value=metric).border = self.thin_border
            value_cell = ws.cell(row=row, column=2, value=formula)
            value_cell.border = self.thin_border
            if unit == 'SAR':
                value_cell.number_format = '#,##0 "SAR"'
            ws.cell(row=row, column=3, value=unit).border = self.thin_border

        # Alert Flags Panel
        ws.merge_cells('A14:D14')
        ws['A14'] = 'ALERT FLAGS'
        ws['A14'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['A14'].fill = PatternFill(start_color='C00000', end_color='C00000', fill_type='solid')

        alert_headers = ['Alert Type', 'Status', 'Count/Value', 'Action Required']
        for col, header in enumerate(alert_headers, 1):
            cell = ws.cell(row=15, column=col, value=header)
            self.apply_header_style(cell)

        alerts = [
            ('Critical Gap', '=IF(Treasury_Calendar!B18<-500000,"YES","NO")',
             '=IF(Treasury_Calendar!B18<-500000,Treasury_Calendar!B18,"-")',
             'Review cash position immediately'),
            ('Escalated Payment (PST2)', '=IF(COUNTIFS(Data_Hub!$N$4:$N$100,"PST2")>0,"YES","NO")',
             '=COUNTIFS(Data_Hub!$N$4:$N$100,"PST2")',
             'Management approval required'),
            ('TD Action Required', '=IF(COUNTIFS(Time_Deposits!$L$4:$L$100,"ACTION REQUIRED")>0,"YES","NO")',
             '=COUNTIFS(Time_Deposits!$L$4:$L$100,"ACTION REQUIRED")',
             'Decide on matured TD'),
            ('Surplus Available', '=IF(Treasury_Calendar!B18>1000000,"YES","NO")',
             '=IF(Treasury_Calendar!B18>1000000,Treasury_Calendar!B18,"-")',
             'Consider rolling to TD'),
        ]

        alert_colors = {
            'Critical Gap': 'FF0000',
            'Escalated Payment (PST2)': 'ED7D31',
            'TD Action Required': 'FFC000',
            'Surplus Available': '70AD47',
        }

        for row, (alert_type, status_formula, value_formula, action) in enumerate(alerts, 16):
            type_cell = ws.cell(row=row, column=1, value=alert_type)
            type_cell.fill = PatternFill(start_color=alert_colors[alert_type],
                                        end_color=alert_colors[alert_type], fill_type='solid')
            type_cell.border = self.thin_border

            ws.cell(row=row, column=2, value=status_formula).border = self.thin_border
            ws.cell(row=row, column=3, value=value_formula).border = self.thin_border
            ws.cell(row=row, column=4, value=action).border = self.thin_border

        # Today's Action List
        ws.merge_cells('F4:H4')
        ws['F4'] = "TODAY'S ACTION LIST"
        ws['F4'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['F4'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        action_headers = ['Item', 'Type', 'Amount (SAR)']
        for col, header in enumerate(action_headers, 6):
            cell = ws.cell(row=5, column=col, value=header)
            self.apply_header_style(cell)

        # Placeholder action items
        action_items = [
            ('Payments due today', 'AP', '=SUMIFS(Data_Hub!$M$4:$M$100,Data_Hub!$H$4:$H$100,TODAY())'),
            ('TDs maturing today', 'TD', '=SUMIFS(Time_Deposits!$K$4:$K$100,Time_Deposits!$F$4:$F$100,TODAY())'),
            ('Escalated items (PST2)', 'Escalation', '=SUMIFS(Data_Hub!$M$4:$M$100,Data_Hub!$N$4:$N$100,"PST2")'),
        ]

        for row, (item, item_type, formula) in enumerate(action_items, 6):
            ws.cell(row=row, column=6, value=item).border = self.thin_border
            ws.cell(row=row, column=7, value=item_type).border = self.thin_border
            amount_cell = ws.cell(row=row, column=8, value=formula)
            amount_cell.number_format = self.currency_format
            amount_cell.border = self.thin_border

        # Weekly Summary Chart placeholder
        ws.merge_cells('F14:H14')
        ws['F14'] = 'WEEKLY CASH FLOW SUMMARY'
        ws['F14'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['F14'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        summary_headers = ['Week', 'Outflows', 'Inflows']
        for col, header in enumerate(summary_headers, 6):
            cell = ws.cell(row=15, column=col, value=header)
            self.apply_header_style(cell)

        weeks = ['This Week', 'Week +1', 'Week +2', 'Week +3']
        for row, week in enumerate(weeks, 16):
            ws.cell(row=row, column=6, value=week).border = self.thin_border
            ws.cell(row=row, column=7, value=f'=Treasury_Calendar!{get_column_letter(row-14)}11').border = self.thin_border
            ws.cell(row=row, column=7).number_format = self.currency_format
            ws.cell(row=row, column=8, value=f'=Treasury_Calendar!{get_column_letter(row-14)}18').border = self.thin_border
            ws.cell(row=row, column=8).number_format = self.currency_format

        # Column widths
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 35
        ws.column_dimensions['E'].width = 3
        ws.column_dimensions['F'].width = 25
        ws.column_dimensions['G'].width = 15
        ws.column_dimensions['H'].width = 18

        # Conditional formatting for alert status
        ws.conditional_formatting.add('B16:B19',
            CellIsRule(operator='equal', formula=['"YES"'],
                      fill=PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid'),
                      font=Font(color='9C0006', bold=True)))
        ws.conditional_formatting.add('B16:B19',
            CellIsRule(operator='equal', formula=['"NO"'],
                      fill=PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid'),
                      font=Font(color='006100')))

    def create_validation_sheet(self):
        """Create Validation & Audit Framework sheet"""
        ws = self.wb.create_sheet("Validation")

        # Title
        ws.merge_cells('A1:D1')
        ws['A1'] = 'VALIDATION & AUDIT FRAMEWORK'
        ws['A1'].font = Font(bold=True, size=14, color='FFFFFF')
        ws['A1'].fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        ws['A1'].alignment = Alignment(horizontal='center')

        # Cross-Check Formulas
        ws.merge_cells('A3:D3')
        ws['A3'] = 'DATA INTEGRITY CHECKS'
        ws['A3'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['A3'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        check_headers = ['Validation Check', 'Formula', 'Result', 'Status']
        for col, header in enumerate(check_headers, 1):
            cell = ws.cell(row=4, column=col, value=header)
            self.apply_header_style(cell)

        checks = [
            ('Payment Total Reconciliation',
             '=SUM(Data_Hub!$M$4:$M$100)=SUM(Payment_Calendar!$D$5:$D$25)',
             '=IF(SUM(Data_Hub!$M$4:$M$100)=SUM(Payment_Calendar!$D$5:$D$25),"PASS","FAIL")',
             'Verify payment calendar matches data hub'),
            ('TD Principal Balance',
             '=SUM(Time_Deposits!$N$4:$N$100)',
             '=SUM(Time_Deposits!$N$4:$N$100)',
             'Total TD principal'),
            ('Missing Required Fields',
             '=COUNTBLANK(Data_Hub!$A$4:$A$100)+COUNTBLANK(Data_Hub!$G$4:$G$100)',
             '=IF(COUNTBLANK(Data_Hub!$A$4:$A$100)+COUNTBLANK(Data_Hub!$G$4:$G$100)=0,"COMPLETE","INCOMPLETE")',
             'Check for missing payment IDs or dates'),
            ('Invalid Status Codes',
             '=COUNTIF(Data_Hub!$N$4:$N$100,"<>PND")-COUNTIF(Data_Hub!$N$4:$N$100,"PAID")-COUNTIF(Data_Hub!$N$4:$N$100,"PST*")-COUNTIF(Data_Hub!$N$4:$N$100,"URG")-COUNTIF(Data_Hub!$N$4:$N$100,"CAN")',
             '=IF(COUNTIF(Data_Hub!$N$4:$N$100,"<>PND")-COUNTIF(Data_Hub!$N$4:$N$100,"PAID")-SUMPRODUCT((LEFT(Data_Hub!$N$4:$N$100,3)="PST")*1)-COUNTIF(Data_Hub!$N$4:$N$100,"URG")-COUNTIF(Data_Hub!$N$4:$N$100,"CAN")<=0,"VALID","INVALID")',
             'Verify all status codes are valid'),
            ('Currency Code Validation',
             '=SUMPRODUCT((ISERROR(MATCH(Data_Hub!$K$4:$K$100,Exchange_Rates!$A$4:$A$11,0)))*1)',
             '=IF(SUMPRODUCT((ISERROR(MATCH(Data_Hub!$K$4:$K$100,Exchange_Rates!$A$4:$A$11,0)))*1)=0,"VALID","INVALID")',
             'All currency codes must exist in exchange rates'),
        ]

        for row, (check_name, formula, result, desc) in enumerate(checks, 5):
            ws.cell(row=row, column=1, value=check_name).border = self.thin_border
            ws.cell(row=row, column=2, value=formula).border = self.thin_border
            ws.cell(row=row, column=2).font = Font(size=9)
            result_cell = ws.cell(row=row, column=3, value=result)
            result_cell.border = self.thin_border
            ws.cell(row=row, column=4, value=desc).border = self.thin_border

        # Conditional formatting for validation results
        ws.conditional_formatting.add('C5:C10',
            CellIsRule(operator='equal', formula=['"PASS"'],
                      fill=PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid'),
                      font=Font(color='006100', bold=True)))
        ws.conditional_formatting.add('C5:C10',
            CellIsRule(operator='equal', formula=['"FAIL"'],
                      fill=PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid'),
                      font=Font(color='9C0006', bold=True)))
        ws.conditional_formatting.add('C5:C10',
            CellIsRule(operator='equal', formula=['"VALID"'],
                      fill=PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid'),
                      font=Font(color='006100', bold=True)))
        ws.conditional_formatting.add('C5:C10',
            CellIsRule(operator='equal', formula=['"INVALID"'],
                      fill=PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid'),
                      font=Font(color='9C0006', bold=True)))

        # Period Selector Section
        ws.merge_cells('A13:D13')
        ws['A13'] = 'PERIOD SELECTOR CONFIGURATION'
        ws['A13'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['A13'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        selector_headers = ['Selector', 'Options', 'Current Value', 'Description']
        for col, header in enumerate(selector_headers, 1):
            cell = ws.cell(row=14, column=col, value=header)
            self.apply_header_style(cell)

        selectors = [
            ('Period Type', 'Weekly / Monthly / Quarterly / Yearly', 'Weekly', 'Changes filter scope'),
            ('Week ID', '01-52', '50', 'Filters to specific Saudi week (Sunday start)'),
            ('Month', 'Jan-Dec', 'Dec', 'Filters to calendar month'),
            ('Quarter', 'Q1-Q4', 'Q4', 'Filters to quarter'),
            ('Year', '2024, 2025, ...', '2024', 'Filters to full year'),
        ]

        for row, (selector, options, current, desc) in enumerate(selectors, 15):
            ws.cell(row=row, column=1, value=selector).border = self.thin_border
            ws.cell(row=row, column=2, value=options).border = self.thin_border

            # Add data validation for selectors
            if selector == 'Period Type':
                dv = DataValidation(type="list", formula1='"Weekly,Monthly,Quarterly,Yearly"')
                ws.add_data_validation(dv)
                dv.add(f'C{row}')
            elif selector == 'Month':
                dv = DataValidation(type="list", formula1='"Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec"')
                ws.add_data_validation(dv)
                dv.add(f'C{row}')
            elif selector == 'Quarter':
                dv = DataValidation(type="list", formula1='"Q1,Q2,Q3,Q4"')
                ws.add_data_validation(dv)
                dv.add(f'C{row}')

            ws.cell(row=row, column=3, value=current).border = self.thin_border
            ws.cell(row=row, column=4, value=desc).border = self.thin_border

        # System Information
        ws.merge_cells('A22:D22')
        ws['A22'] = 'SYSTEM INFORMATION'
        ws['A22'].font = Font(bold=True, size=12, color='FFFFFF')
        ws['A22'].fill = PatternFill(start_color='2E75B6', end_color='2E75B6', fill_type='solid')

        sys_info = [
            ('Workbook Version', '1.0.0'),
            ('Created Date', datetime.now().strftime('%Y-%m-%d')),
            ('Last Modified', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ('Base Currency', 'SAR'),
            ('Week Configuration', 'Saudi (Sunday Start)'),
            ('Payment Day', 'Wednesday (Day 4)'),
        ]

        for row, (key, value) in enumerate(sys_info, 23):
            ws.cell(row=row, column=1, value=key).border = self.thin_border
            ws.cell(row=row, column=1).font = Font(bold=True)
            ws.cell(row=row, column=2, value=value).border = self.thin_border

        # Column widths
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 50
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 40


def main():
    """Generate the Treasury Management System workbook"""
    generator = TreasuryWorkbookGenerator()
    output_path = generator.create_workbook()
    print(f"\nWorkbook created successfully!")
    print(f"Location: {output_path}")
    print("\nSheets created:")
    print("  1. Configuration - System parameters and settings")
    print("  2. Exchange_Rates - Currency conversion rates")
    print("  3. Data_Hub - Master data (single source of truth)")
    print("  4. Time_Deposits - TD tracking with analytics")
    print("  5. Payment_Calendar - Wednesday payment schedule")
    print("  6. Treasury_Calendar - Cash position view")
    print("  7. Dashboard - Executive summary and alerts")
    print("  8. Validation - Data integrity checks")


if __name__ == "__main__":
    main()
