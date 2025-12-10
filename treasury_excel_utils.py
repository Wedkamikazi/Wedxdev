"""
Treasury Excel Utilities
Helper functions for interacting with the Treasury Management System Excel workbook.
"""

import os
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


class TreasuryExcelManager:
    """Manager class for Treasury Management System Excel operations"""

    def __init__(self, workbook_path: str = None):
        """Initialize with path to the Treasury workbook"""
        if workbook_path is None:
            workbook_path = os.path.join(
                os.path.dirname(__file__),
                'Treasury_Management_System.xlsx'
            )
        self.workbook_path = workbook_path
        self._wb = None

    @property
    def workbook(self):
        """Lazy load workbook"""
        if self._wb is None:
            if os.path.exists(self.workbook_path):
                self._wb = load_workbook(self.workbook_path)
            else:
                raise FileNotFoundError(f"Treasury workbook not found: {self.workbook_path}")
        return self._wb

    def save(self):
        """Save the workbook"""
        if self._wb:
            self._wb.save(self.workbook_path)

    def close(self):
        """Close the workbook"""
        if self._wb:
            self._wb.close()
            self._wb = None

    # ========== WEDNESDAY SNAP ENGINE ==========

    @staticmethod
    def calculate_target_wednesday(due_date: datetime, vendor_tier: int,
                                   priority_flag: str = 'NORMAL') -> datetime:
        """
        Calculate the target Wednesday payment date based on vendor tier.

        Args:
            due_date: The original due date
            vendor_tier: 1=Critical, 2=Standard, 3=Flexible
            priority_flag: URGENT, PAYROLL, or NORMAL

        Returns:
            The calculated Wednesday payment date
        """
        # URGENT and PAYROLL bypass Wednesday snap
        if priority_flag in ('URGENT', 'PAYROLL'):
            return due_date

        # Find the day of week (0=Monday, 6=Sunday)
        # Convert to Saudi week (0=Sunday)
        day_of_week = (due_date.weekday() + 1) % 7  # 0=Sunday, 1=Monday, ..., 6=Saturday
        wednesday_offset = 3  # Wednesday is day 3 in Saudi week

        if day_of_week == wednesday_offset:
            # Due date is Wednesday - pay on same day
            return due_date

        if vendor_tier == 1:
            # Tier 1 (Critical): Pay BEFORE due date (previous Wednesday)
            days_since_wednesday = (day_of_week - wednesday_offset) % 7
            if days_since_wednesday == 0:
                days_since_wednesday = 7
            return due_date - timedelta(days=days_since_wednesday)
        else:
            # Tier 2-3 (Standard/Flexible): Pay AFTER due date (next Wednesday)
            days_until_wednesday = (wednesday_offset - day_of_week) % 7
            if days_until_wednesday == 0:
                days_until_wednesday = 7
            return due_date + timedelta(days=days_until_wednesday)

    @staticmethod
    def get_week_id(date: datetime) -> int:
        """
        Get the Saudi week number (Sunday start).

        Args:
            date: The date to get week number for

        Returns:
            Week number (1-52)
        """
        # ISO week starts Monday, Saudi week starts Sunday
        # Adjust by adding 1 day to align Sunday as start
        adjusted_date = date + timedelta(days=1)
        return adjusted_date.isocalendar()[1]

    # ========== PAYMENT STATUS ENGINE ==========

    @staticmethod
    def determine_payment_status(target_wednesday: datetime,
                                 current_status: str,
                                 postpone_count: int,
                                 is_paid: bool = False) -> Tuple[str, int]:
        """
        Determine the payment status based on the state machine logic.

        Args:
            target_wednesday: The target payment date
            current_status: Current status code
            postpone_count: Current postpone count
            is_paid: Whether payment has been executed

        Returns:
            Tuple of (new_status, new_postpone_count)
        """
        today = datetime.now().date()
        target_date = target_wednesday.date() if isinstance(target_wednesday, datetime) else target_wednesday

        if is_paid:
            return ('PAID', postpone_count)

        if current_status == 'CAN':
            return ('CAN', postpone_count)

        if current_status == 'URG':
            return ('URG', postpone_count)

        # Auto-postponement logic
        if target_date < today and current_status in ('PND', 'PST1', 'PST2'):
            new_count = postpone_count + 1
            if new_count == 1:
                return ('PST1', new_count)
            else:
                return ('PST2', new_count)

        return (current_status, postpone_count)

    @staticmethod
    def calculate_next_wednesday(from_date: datetime = None) -> datetime:
        """
        Calculate the next Wednesday from a given date.

        Args:
            from_date: Starting date (defaults to today)

        Returns:
            Next Wednesday date
        """
        if from_date is None:
            from_date = datetime.now()

        # Convert to Saudi week day
        day_of_week = (from_date.weekday() + 1) % 7  # 0=Sunday
        wednesday = 3

        days_until_wednesday = (wednesday - day_of_week) % 7
        if days_until_wednesday == 0:
            days_until_wednesday = 7

        return from_date + timedelta(days=days_until_wednesday)

    # ========== DATA HUB OPERATIONS ==========

    def add_payment(self, payment_data: Dict) -> str:
        """
        Add a new payment to the Data Hub.

        Args:
            payment_data: Dictionary with payment details

        Returns:
            The generated Payment_ID
        """
        ws = self.workbook['Data_Hub']

        # Find next empty row
        next_row = 4
        while ws.cell(row=next_row, column=1).value is not None:
            next_row += 1

        # Generate Payment_ID
        payment_id = f"PAY-{datetime.now().strftime('%Y')}-{next_row-3:03d}"

        # Required fields with defaults
        defaults = {
            'Payment_ID': payment_id,
            'Type_Code': 'AP',
            'Category': 'OPEX',
            'Vendor_Tier': 2,
            'Currency_Code': 'SAR',
            'FX_Rate': 1.0,
            'Payment_Status': 'PND',
            'Postpone_Count': 0,
            'Priority_Flag': 'NORMAL',
            'Created_Date': datetime.now(),
            'Created_By': 'System',
        }

        # Merge with provided data
        data = {**defaults, **payment_data}

        # Calculate Target_Wednesday
        if 'Raw_Due_Date' in data:
            data['Target_Wednesday'] = self.calculate_target_wednesday(
                data['Raw_Due_Date'],
                data.get('Vendor_Tier', 2),
                data.get('Priority_Flag', 'NORMAL')
            )

        # Calculate Amount_SAR
        if 'Amount_Original' in data and 'FX_Rate' in data:
            data['Amount_SAR'] = data['Amount_Original'] * data['FX_Rate']

        # Column mapping
        column_map = {
            'Payment_ID': 1, 'Type_Code': 2, 'Category': 3,
            'Vendor_Name': 4, 'Vendor_Tier': 5, 'Contact': 6,
            'Raw_Due_Date': 7, 'Target_Wednesday': 8, 'Value_Date': 9,
            'Amount_Original': 10, 'Currency_Code': 11, 'FX_Rate': 12, 'Amount_SAR': 13,
            'Payment_Status': 14, 'Postpone_Count': 15, 'Last_Action_Date': 16, 'Priority_Flag': 17,
            'Created_Date': 18, 'Created_By': 19, 'Modified_Date': 20, 'Modified_By': 21, 'Notes': 22,
        }

        # Write data
        for field, col in column_map.items():
            if field in data:
                ws.cell(row=next_row, column=col, value=data[field])

        self.save()
        return payment_id

    def get_payments_by_status(self, status: str) -> List[Dict]:
        """
        Get all payments with a specific status.

        Args:
            status: Status code (PND, PAID, PST1, PST2, URG, CAN)

        Returns:
            List of payment dictionaries
        """
        ws = self.workbook['Data_Hub']
        payments = []

        column_headers = [
            'Payment_ID', 'Type_Code', 'Category',
            'Vendor_Name', 'Vendor_Tier', 'Contact',
            'Raw_Due_Date', 'Target_Wednesday', 'Value_Date',
            'Amount_Original', 'Currency_Code', 'FX_Rate', 'Amount_SAR',
            'Payment_Status', 'Postpone_Count', 'Last_Action_Date', 'Priority_Flag',
            'Created_Date', 'Created_By', 'Modified_Date', 'Modified_By', 'Notes',
        ]

        row = 4
        while ws.cell(row=row, column=1).value is not None:
            if ws.cell(row=row, column=14).value == status:
                payment = {}
                for col, header in enumerate(column_headers, 1):
                    payment[header] = ws.cell(row=row, column=col).value
                payments.append(payment)
            row += 1

        return payments

    def get_payments_due_this_wednesday(self) -> List[Dict]:
        """Get all payments due this Wednesday"""
        next_wed = self.calculate_next_wednesday()
        ws = self.workbook['Data_Hub']
        payments = []

        column_headers = [
            'Payment_ID', 'Type_Code', 'Category',
            'Vendor_Name', 'Vendor_Tier', 'Contact',
            'Raw_Due_Date', 'Target_Wednesday', 'Value_Date',
            'Amount_Original', 'Currency_Code', 'FX_Rate', 'Amount_SAR',
            'Payment_Status', 'Postpone_Count', 'Last_Action_Date', 'Priority_Flag',
            'Created_Date', 'Created_By', 'Modified_Date', 'Modified_By', 'Notes',
        ]

        row = 4
        while ws.cell(row=row, column=1).value is not None:
            target_wed = ws.cell(row=row, column=8).value
            status = ws.cell(row=row, column=14).value
            if target_wed and status not in ('PAID', 'CAN'):
                if isinstance(target_wed, datetime):
                    if target_wed.date() == next_wed.date():
                        payment = {}
                        for col, header in enumerate(column_headers, 1):
                            payment[header] = ws.cell(row=row, column=col).value
                        payments.append(payment)
            row += 1

        return payments

    def update_payment_status(self, payment_id: str, new_status: str,
                              value_date: datetime = None) -> bool:
        """
        Update the status of a payment.

        Args:
            payment_id: The payment ID to update
            new_status: New status code
            value_date: Actual payment date (for PAID status)

        Returns:
            True if updated successfully
        """
        ws = self.workbook['Data_Hub']

        row = 4
        while ws.cell(row=row, column=1).value is not None:
            if ws.cell(row=row, column=1).value == payment_id:
                ws.cell(row=row, column=14, value=new_status)
                ws.cell(row=row, column=16, value=datetime.now())
                ws.cell(row=row, column=20, value=datetime.now())
                ws.cell(row=row, column=21, value='System')

                if new_status == 'PAID' and value_date:
                    ws.cell(row=row, column=9, value=value_date)

                self.save()
                return True
            row += 1

        return False

    def run_auto_postponement(self) -> List[Dict]:
        """
        Run the auto-postponement engine for all overdue payments.

        Returns:
            List of payments that were auto-postponed
        """
        ws = self.workbook['Data_Hub']
        postponed = []
        today = datetime.now().date()

        row = 4
        while ws.cell(row=row, column=1).value is not None:
            status = ws.cell(row=row, column=14).value
            target_wed = ws.cell(row=row, column=8).value

            if status in ('PND', 'PST1') and target_wed:
                target_date = target_wed.date() if isinstance(target_wed, datetime) else target_wed
                if target_date < today:
                    # Auto-postpone
                    payment_id = ws.cell(row=row, column=1).value
                    current_count = ws.cell(row=row, column=15).value or 0
                    new_count = current_count + 1

                    # Calculate next Wednesday
                    new_target = self.calculate_next_wednesday()

                    # Update fields
                    ws.cell(row=row, column=8, value=new_target)
                    ws.cell(row=row, column=14, value='PST1' if new_count == 1 else 'PST2')
                    ws.cell(row=row, column=15, value=new_count)
                    ws.cell(row=row, column=16, value=datetime.now())
                    ws.cell(row=row, column=20, value=datetime.now())
                    ws.cell(row=row, column=21, value='Auto-Postpone')

                    postponed.append({
                        'Payment_ID': payment_id,
                        'Previous_Target': target_wed,
                        'New_Target': new_target,
                        'Postpone_Count': new_count,
                    })

            row += 1

        if postponed:
            self.save()

        return postponed

    # ========== TIME DEPOSIT OPERATIONS ==========

    def add_time_deposit(self, td_data: Dict) -> str:
        """
        Add a new Time Deposit to the tracking sheet.

        Args:
            td_data: Dictionary with TD details

        Returns:
            The generated TD_ID
        """
        ws = self.workbook['Time_Deposits']

        # Find next empty row
        next_row = 4
        while ws.cell(row=next_row, column=1).value is not None:
            next_row += 1

        # Generate TD_ID
        td_id = f"TD-{datetime.now().strftime('%Y')}-{next_row-3:03d}"

        # Defaults
        defaults = {
            'TD_ID': td_id,
            'Currency': 'SAR',
            'Rate_Percent': 0.05,
        }

        data = {**defaults, **td_data}

        # Write basic data
        column_map = {
            'TD_ID': 1, 'Bank': 2, 'Account_No': 3, 'Currency': 4,
            'Start_Date': 5, 'Maturity_Date': 6, 'Principal_Original': 7,
            'Rate_Percent': 8,
        }

        for field, col in column_map.items():
            if field in data:
                ws.cell(row=next_row, column=col, value=data[field])

        # Add formulas (these will be calculated by Excel)
        # Days: =F{row}-E{row}
        ws.cell(row=next_row, column=9, value=f'=$F${next_row}-$E${next_row}')
        # Profit: =G*H*I/365
        ws.cell(row=next_row, column=10, value=f'=$G${next_row}*$H${next_row}*$I${next_row}/365')
        # Maturity Amount: =G+J
        ws.cell(row=next_row, column=11, value=f'=$G${next_row}+$J${next_row}')
        # Status formula
        ws.cell(row=next_row, column=12, value=f'=IF($F${next_row}<TODAY(),"CLOSED",IF($F${next_row}=TODAY(),"ACTION REQUIRED","ACTIVE"))')
        # Week ID
        ws.cell(row=next_row, column=13, value=f'=WEEKNUM($F${next_row},2)')

        self.save()
        return td_id

    def get_tds_maturing_today(self) -> List[Dict]:
        """Get all TDs maturing today"""
        ws = self.workbook['Time_Deposits']
        tds = []
        today = datetime.now().date()

        row = 4
        while ws.cell(row=row, column=1).value is not None:
            maturity_date = ws.cell(row=row, column=6).value
            if maturity_date:
                mat_date = maturity_date.date() if isinstance(maturity_date, datetime) else maturity_date
                if mat_date == today:
                    td = {
                        'TD_ID': ws.cell(row=row, column=1).value,
                        'Bank': ws.cell(row=row, column=2).value,
                        'Principal': ws.cell(row=row, column=7).value,
                        'Rate': ws.cell(row=row, column=8).value,
                        'Maturity_Date': maturity_date,
                    }
                    tds.append(td)
            row += 1

        return tds

    # ========== EXCHANGE RATE OPERATIONS ==========

    def get_exchange_rate(self, currency: str) -> float:
        """
        Get the current exchange rate for a currency.

        Args:
            currency: Currency code

        Returns:
            Exchange rate to SAR
        """
        ws = self.workbook['Exchange_Rates']

        row = 4
        while ws.cell(row=row, column=1).value is not None:
            if ws.cell(row=row, column=1).value == currency:
                return ws.cell(row=row, column=2).value
            row += 1

        raise ValueError(f"Currency not found: {currency}")

    def update_exchange_rate(self, currency: str, new_rate: float) -> bool:
        """
        Update an exchange rate.

        Args:
            currency: Currency code
            new_rate: New exchange rate to SAR

        Returns:
            True if updated successfully
        """
        ws = self.workbook['Exchange_Rates']

        row = 4
        while ws.cell(row=row, column=1).value is not None:
            if ws.cell(row=row, column=1).value == currency:
                ws.cell(row=row, column=2, value=new_rate)
                ws.cell(row=row, column=3, value=datetime.now())
                ws.cell(row=row, column=4, value='System')
                self.save()
                return True
            row += 1

        return False

    # ========== REPORTING ==========

    def get_cash_position_summary(self) -> Dict:
        """
        Get a summary of the current cash position.

        Returns:
            Dictionary with cash position metrics
        """
        # Get pending payments
        pending = self.get_payments_by_status('PND')
        pst1 = self.get_payments_by_status('PST1')
        pst2 = self.get_payments_by_status('PST2')

        def safe_sum(items, key):
            total = 0
            for item in items:
                val = item.get(key, 0)
                if isinstance(val, (int, float)):
                    total += val
            return total

        total_pending_sar = safe_sum(pending, 'Amount_SAR')
        total_pst1_sar = safe_sum(pst1, 'Amount_SAR')
        total_pst2_sar = safe_sum(pst2, 'Amount_SAR')

        # Get TDs maturing this week
        tds_today = self.get_tds_maturing_today()
        td_principal_today = safe_sum(tds_today, 'Principal')

        return {
            'pending_payments_count': len(pending),
            'pending_payments_sar': total_pending_sar,
            'postponed_once_count': len(pst1),
            'postponed_once_sar': total_pst1_sar,
            'escalated_count': len(pst2),
            'escalated_sar': total_pst2_sar,
            'tds_maturing_today': len(tds_today),
            'td_principal_today': td_principal_today,
            'total_outflow_required': total_pending_sar + total_pst1_sar + total_pst2_sar,
        }

    def export_payments_to_csv(self, filepath: str, status_filter: str = None) -> int:
        """
        Export payments to CSV file.

        Args:
            filepath: Output file path
            status_filter: Optional status to filter by

        Returns:
            Number of payments exported
        """
        ws = self.workbook['Data_Hub']

        headers = [
            'Payment_ID', 'Type_Code', 'Category',
            'Vendor_Name', 'Vendor_Tier', 'Contact',
            'Raw_Due_Date', 'Target_Wednesday', 'Value_Date',
            'Amount_Original', 'Currency_Code', 'FX_Rate', 'Amount_SAR',
            'Payment_Status', 'Postpone_Count', 'Last_Action_Date', 'Priority_Flag',
            'Created_Date', 'Created_By', 'Modified_Date', 'Modified_By', 'Notes',
        ]

        rows_exported = 0
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

            row = 4
            while ws.cell(row=row, column=1).value is not None:
                status = ws.cell(row=row, column=14).value
                if status_filter is None or status == status_filter:
                    payment = {}
                    for col, header in enumerate(headers, 1):
                        value = ws.cell(row=row, column=col).value
                        if isinstance(value, datetime):
                            value = value.strftime('%Y-%m-%d')
                        payment[header] = value
                    writer.writerow(payment)
                    rows_exported += 1
                row += 1

        return rows_exported


def import_from_csv(manager: TreasuryExcelManager, csv_path: str) -> int:
    """
    Import payments from a CSV file into the Treasury workbook.

    Args:
        manager: TreasuryExcelManager instance
        csv_path: Path to the CSV file

    Returns:
        Number of payments imported
    """
    imported = 0

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert date strings
            payment_data = {}
            for key, value in row.items():
                if key and value:
                    if 'Date' in key or key == 'Target_Wednesday':
                        try:
                            payment_data[key] = datetime.strptime(value, '%Y-%m-%d')
                        except ValueError:
                            payment_data[key] = value
                    elif key in ('Amount_Original', 'Amount_SAR', 'FX_Rate'):
                        try:
                            payment_data[key] = float(value)
                        except ValueError:
                            payment_data[key] = value
                    elif key in ('Vendor_Tier', 'Postpone_Count'):
                        try:
                            payment_data[key] = int(value)
                        except ValueError:
                            payment_data[key] = value
                    else:
                        payment_data[key] = value

            manager.add_payment(payment_data)
            imported += 1

    return imported


# Convenience functions
def get_next_wednesday() -> datetime:
    """Get the next Wednesday date"""
    return TreasuryExcelManager.calculate_next_wednesday()


def calculate_wednesday_for_payment(due_date: datetime, vendor_tier: int = 2,
                                   priority: str = 'NORMAL') -> datetime:
    """
    Calculate the Wednesday payment date for a given due date.

    Args:
        due_date: Original due date
        vendor_tier: 1=Critical, 2=Standard, 3=Flexible
        priority: URGENT, PAYROLL, or NORMAL

    Returns:
        Calculated Wednesday payment date
    """
    return TreasuryExcelManager.calculate_target_wednesday(due_date, vendor_tier, priority)


if __name__ == "__main__":
    # Example usage
    manager = TreasuryExcelManager()

    print("=== Treasury Excel Manager ===\n")

    # Get cash position summary
    summary = manager.get_cash_position_summary()
    print("Cash Position Summary:")
    for key, value in summary.items():
        if 'sar' in key.lower():
            print(f"  {key}: {value:,.2f} SAR")
        else:
            print(f"  {key}: {value}")

    print(f"\nNext Wednesday: {get_next_wednesday().strftime('%Y-%m-%d')}")

    # Example Wednesday calculation
    test_date = datetime(2024, 12, 16)
    for tier in [1, 2, 3]:
        wed = calculate_wednesday_for_payment(test_date, tier)
        print(f"Due {test_date.strftime('%Y-%m-%d')} (Tier {tier}): Pay on {wed.strftime('%Y-%m-%d')}")

    manager.close()
