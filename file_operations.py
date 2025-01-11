from datetime import datetime
import csv
import os

class FileOperations:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_paths = {
            'BS-SALAM': os.path.join(self.base_dir, 'data/bank_statements/SALAM/BS_SALAM_CURRENT.csv'),
            'BS-MVNO': os.path.join(self.base_dir, 'data/bank_statements/mvno/BS_MVNO_CURRENT.csv'),
            'CNP-SALAM': os.path.join(self.base_dir, 'data/cnp/SALAM/CNP_SALAM_CURRENT.csv'),
            'CNP-MVNO': os.path.join(self.base_dir, 'data/cnp/mvno/CNP_MVNO_CURRENT.csv'),
            'Treasury': os.path.join(self.base_dir, 'data/treasury/TREASURY_CURRENT.csv')
        }
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            'data',
            'data/bank_statements',
            'data/bank_statements/SALAM',
            'data/bank_statements/mvno',
            'data/cnp',
            'data/cnp/SALAM',
            'data/cnp/mvno',
            'data/treasury'
        ]
        for directory in directories:
            dir_path = os.path.join(self.base_dir, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                # Ensure write permissions
                os.chmod(dir_path, 0o777)

        # Ensure files exist with proper permissions
        for file_key, file_path in self.file_paths.items():
            if not os.path.exists(file_path):
                # Create empty CSV with headers
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['reference', 'amount', 'date', 'status', 'timestamp'])
                # Set file permissions
                os.chmod(file_path, 0o666)

    def verify_payment(self, payment_data):
        """Verify payment across all relevant sheets"""
        results = {
            'matches': False,
            'details': [],
            'files': [],
            'matching_records': []
        }

        # Step 1: Check Bank Statement
        bs_result = self._check_bank_statement(payment_data)
        if bs_result['matches']:
            results['matches'] = True
            for match in bs_result['matches']:
                record = match['record']
                results['details'].append(
                    f"Match found in {match['file']}:\n"
                    f"  Reference: {record['reference']}\n"
                    f"  Amount: {record['amount']}\n"
                    f"  Date: {record['date']}\n"
                    f"  Status: {record['status']}\n"
                    f"  Timestamp: {record['timestamp']}"
                )
                results['matching_records'].append(record)
            results['files'].append(f"BS-{payment_data['company']}")

        # Add bank statement messages
        if bs_result.get('messages'):
            results['details'].extend(bs_result['messages'])

        # Step 2: Check CNP if needed (old payment)
        cnp_result = {'matches': [], 'messages': []}  # Initialize with empty result
        if self._is_old_payment(payment_data['date']):
            cnp_result = self._check_cnp(payment_data)
            if cnp_result['matches']:
                results['matches'] = True
                for match in cnp_result['matches']:
                    record = match['record']
                    results['details'].append(
                        f"Match found in {match['file']}:\n"
                        f"  Reference: {record['reference']}\n"
                        f"  Amount: {record['amount']}\n"
                        f"  Date: {record['date']}\n"
                        f"  Status: {record['status']}\n"
                        f"  Timestamp: {record['timestamp']}"
                    )
                    results['matching_records'].append(record)
                results['files'].append(f"CNP-{payment_data['company']}")

        # Add CNP messages
        if cnp_result.get('messages'):
            results['details'].extend(cnp_result['messages'])

        return results

    def _check_bank_statement(self, payment_data):
        """Check payment in relevant bank statement"""
        file_key = f"BS-{payment_data['company']}"
        return self._check_file(file_key, payment_data)

    def _check_cnp(self, payment_data):
        """Check payment in relevant CNP file"""
        file_key = f"CNP-{payment_data['company']}"
        return self._check_file(file_key, payment_data)

    def _check_file(self, file_key, payment_data):
        """Check payment in specific file"""
        results = {
            'matches': [],
            'messages': []
        }

        if file_key not in self.file_paths:
            results['messages'].append(f"Invalid file key: {file_key}")
            return results

        file_path = self.file_paths[file_key]
        try:
            if not os.path.exists(file_path):
                results['messages'].append(f"File not found: {file_path}")
                return results

            print(f"Checking file: {file_path}")  # Debug print
            with open(file_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    print(f"Checking row: {row}")  # Debug print
                    if self._is_matching_record(row, payment_data):
                        results['matches'].append({
                            'file': file_key,
                            'record': row
                        })
        except Exception as e:
            results['messages'].append(f"Error reading {file_key}: {str(e)}")
            print(f"Error: {str(e)}")  # Debug print

        return results

    def _is_matching_record(self, record, payment_data):
        """Check if record matches payment data"""
        try:
            # Match reference number (exact match required)
            if record['reference'].strip() != payment_data['reference'].strip():
                return False

            # Match amount (with threshold handling)
            amount = float(record['amount'])
            payment_amount = float(payment_data['amount'])
            if amount > 15000:
                # 1% tolerance for amounts over 15000
                difference = abs(amount - payment_amount) / amount
                if difference > 0.01:
                    return False
            elif amount != payment_amount:
                return False

            return True
        except (KeyError, ValueError) as e:
            return False

    def _is_old_payment(self, payment_date):
        """Check if payment is from previous month"""
        payment_date = datetime.strptime(payment_date, '%Y-%m-%d')
        current_date = datetime.now()
        
        return (payment_date.year < current_date.year or 
                payment_date.month < current_date.month)

    def get_file_path(self, file_key):
        """Get absolute path for a file"""
        return self.file_paths.get(file_key)

    def open_file(self, file_key):
        """Get the path for a file and ensure its directory exists"""
        if file_key not in self.file_paths:
            raise ValueError(f"Invalid file key: {file_key}")
            
        file_path = self.file_paths[file_key]
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return file_path

    def save_payment(self, payment_data):
        """Save payment to Treasury with Under Process status"""
        try:
            file_path = self.file_paths['Treasury']
            
            # Create Treasury file with headers if it doesn't exist
            if not os.path.exists(file_path):
                with open(file_path, 'w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary'])
                    writer.writeheader()
            
            # Append payment data to Treasury
            with open(file_path, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary'])
                writer.writerow({
                    'reference': payment_data['reference'],
                    'amount': payment_data['amount'],
                    'date': payment_data['date'],
                    'status': 'Under Process',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'company': payment_data['company'],
                    'beneficiary': payment_data['beneficiary']
                })
            return True, "Payment added to Treasury successfully"
        except Exception as e:
            error_msg = f"Error saving to Treasury: {str(e)}"
            return False, error_msg
