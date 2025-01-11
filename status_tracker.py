from datetime import datetime
import csv
import os

class StatusTracker:
    def __init__(self):
        """Initialize status tracker"""
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Base directory: {self.base_dir}")
        
        # Update file paths
        self.treasury_file = os.path.join(self.base_dir, 'data', 'treasury', 'TREASURY_CURRENT.csv')
        
        # Bank Statement files
        self.bs_files = {
            'SALAM': os.path.join(self.base_dir, 'data', 'bank_statements', 'SALAM', 'BS_SALAM_CURRENT.csv'),
            'MVNO': os.path.join(self.base_dir, 'data', 'bank_statements', 'MVNO', 'BS_MVNO_CURRENT.csv')
        }
        
        # CNP (Check Not Presented) files
        self.cnp_files = {
            'SALAM': os.path.join(self.base_dir, 'data', 'cnp', 'SALAM', 'CNP_SALAM_CURRENT.csv'),
            'MVNO': os.path.join(self.base_dir, 'data', 'cnp', 'MVNO', 'CNP_MVNO_CURRENT.csv')
        }
        
        self.delay_threshold = 30  # days to consider payment as previous month
        
        # Ensure directories exist
        self._ensure_directories()
        
    def is_previous_month_payment(self, payment_date_str):
        """Check if payment is from previous month"""
        try:
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            
            # Calculate days difference
            days_diff = (current_date - payment_date).days
            return days_diff >= self.delay_threshold
        except Exception as e:
            print(f"Error parsing date {payment_date_str}: {e}")
            return False
            
    def check_payment_status(self, payment, company=None):
        """
        Check payment status in BS and CNP files based on payment date
        Returns tuple: (found_status, found_in, company)
        """
        reference = payment['reference'].strip()
        try:
            payment_amount = float(payment.get('amount', '0').strip())
        except ValueError:
            return None, None, None
            
        payment_date = payment.get('date', '').strip()
        is_old_payment = self.is_previous_month_payment(payment_date)
        companies = [company] if company else ['SALAM', 'MVNO']
        
        print(f"\nChecking payment: {reference}")
        print(f"Amount: {payment_amount}")
        print(f"Date: {payment_date}")
        print(f"Is old payment: {is_old_payment}")
        
        for comp in companies:
            # For old payments, check CNP first
            if is_old_payment:
                # Check CNP
                cnp_status = self.check_file_for_payment(
                    self.cnp_files[comp], reference, payment_amount
                )
                if cnp_status:
                    return 'CNP', 'CNP', comp
                    
                # Fallback to BS
                bs_status = self.check_file_for_payment(
                    self.bs_files[comp], reference, payment_amount
                )
                if bs_status and bs_status.lower() == 'completed':
                    return 'Paid', 'BS', comp
                    
            # For current payments, check BS first
            else:
                # Check BS
                bs_status = self.check_file_for_payment(
                    self.bs_files[comp], reference, payment_amount
                )
                if bs_status and bs_status.lower() == 'completed':
                    return 'Paid', 'BS', comp
                    
                # Fallback to CNP
                cnp_status = self.check_file_for_payment(
                    self.cnp_files[comp], reference, payment_amount
                )
                if cnp_status:
                    return 'CNP', 'CNP', comp
                    
        return None, None, None
        
    def check_file_for_payment(self, file_path, reference, amount):
        """Check if payment exists in given file and return its status"""
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if (row['reference'].strip() == reference and 
                        abs(float(row['amount'].strip()) - amount) < 0.01):
                        return row.get('status', '').strip()
        except Exception as e:
            print(f"Error checking file {file_path}: {e}")
            
        return None
        
    def update_all_statuses(self):
        """Update status for all payments in Treasury"""
        results = {
            'updated': 0,
            'errors': 0,
            'details': []
        }
        
        print("\n=== Starting Status Update ===")
        
        if not os.path.exists(self.treasury_file):
            print("Treasury file not found")
            results['details'].append("Treasury file not found")
            return results
            
        try:
            # Read all payments from Treasury
            payments_to_update = []
            with open(self.treasury_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                payments = list(reader)
                
            if not payments:
                print("No payments found in Treasury")
                results['details'].append("No payments found in Treasury")
                return results
            
            print(f"\nFound {len(payments)} payments in Treasury")
            
            # Check each payment's status
            for payment in payments:
                try:
                    reference = payment['reference'].strip()
                    current_status = payment.get('status', '').strip()
                    company = payment.get('company', '').strip()
                    
                    print(f"\nChecking Treasury payment: {reference}")
                    print(f"Current Status: {current_status}")
                    
                    # Skip if already paid
                    if current_status == 'Paid':
                        print(f"Skipping {reference} - already Paid")
                        continue
                    
                    # Check status in BS/CNP based on date
                    new_status, found_in, found_company = self.check_payment_status(payment, company)
                    
                    if new_status:
                        print(f"Found in {found_in} for {found_company}")
                        update_data = {
                            'reference': reference,
                            'old_status': current_status,
                            'new_status': new_status,
                            'company': found_company if not company else company,
                            'details': [f"Found in {found_in}-{found_company}"]
                        }
                        payments_to_update.append(update_data)
                    else:
                        print(f"No matching payment found")
                                
                except Exception as e:
                    print(f"Error processing payment {reference}: {str(e)}")
                    results['errors'] += 1
                    results['details'].append(f"Error checking {reference}: {str(e)}")
            
            # Update Treasury file if needed
            if payments_to_update:
                print(f"\nUpdating {len(payments_to_update)} payments in Treasury...")
                
                # Read current Treasury content
                with open(self.treasury_file, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    all_rows = list(reader)
                    fieldnames = reader.fieldnames
                
                # Update statuses and companies
                for row in all_rows:
                    for update in payments_to_update:
                        if row['reference'].strip() == update['reference']:
                            print(f"Updating {row['reference']}:")
                            print(f"  Status: {row['status']} -> {update['new_status']}")
                            print(f"  Company: {row.get('company', '')} -> {update['company']}")
                            
                            row['status'] = update['new_status']
                            if not row.get('company'):
                                row['company'] = update['company']
                            row['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Write back to Treasury
                with open(self.treasury_file, 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_rows)
                
                results['updated'] = len(payments_to_update)
                for update in payments_to_update:
                    msg = f"Updated {update['reference']}: {update['old_status']} -> {update['new_status']}"
                    if update.get('company'):
                        msg += f" (Company: {update['company']})"
                    print(msg)
                    results['details'].append(msg)
            else:
                print("No payments needed updating")
                results['details'].append("No payments needed updating")
            
            return results
            
        except Exception as e:
            print(f"Error in update_all_statuses: {str(e)}")
            results['errors'] += 1
            results['details'].append(f"Error updating statuses: {str(e)}")
            return results

    def create_empty_file(self, file_path):
        """Create new file with headers"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        headers = ['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary']
        with open(file_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            'data/treasury',
            'data/bank_statements/SALAM',
            'data/bank_statements/MVNO',
            'data/cnp/SALAM',
            'data/cnp/MVNO'
        ]
        for directory in directories:
            dir_path = os.path.join(self.base_dir, directory)
            os.makedirs(dir_path, exist_ok=True)
