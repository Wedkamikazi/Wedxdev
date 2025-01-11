from datetime import datetime
import csv
import os

class ExceptionHandler:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.exception_file = os.path.join(self.base_dir, 'data/exceptions/EXCEPTION_LOG.csv')
        self.audit_file = os.path.join(self.base_dir, 'data/exceptions/AUDIT_LOG.csv')
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure exception directory exists"""
        os.makedirs(os.path.dirname(self.exception_file), exist_ok=True)
        
    def log_exception(self, data):
        """Log exception details"""
        exception_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'reference': 'N/A' if not data.get('reference') else data['reference'],
            'type': data.get('type', 'Unknown'),
            'description': data.get('description', ''),
            'status': 'Open',
            'resolution': ''
        }
        
        self._write_to_exception_log(exception_data)
        self._write_to_audit_log({
            'action': 'Exception_Logged',
            'reference': exception_data['reference'],
            'details': f"Exception: {exception_data['type']} - {exception_data['description']}"
        })
        
        return exception_data

    def resolve_exception(self, reference, resolution_data):
        """Resolve an existing exception"""
        exceptions = []
        updated = False
        
        # Read existing exceptions
        if os.path.exists(self.exception_file):
            with open(self.exception_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['reference'] == reference and row['status'] == 'Open':
                        row.update({
                            'status': 'Resolved',
                            'resolution': resolution_data.get('resolution', '')
                        })
                        updated = True
                    exceptions.append(row)
        
        if updated:
            # Write back all exceptions
            with open(self.exception_file, 'w', newline='') as file:
                if exceptions:
                    writer = csv.DictWriter(file, fieldnames=exceptions[0].keys())
                    writer.writeheader()
                    writer.writerows(exceptions)
            
            # Log resolution to audit
            self._write_to_audit_log({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'action': 'Exception_Resolved',
                'reference': reference,
                'details': f"Resolution: {resolution_data.get('resolution', '')}"
            })
            
        return updated

    def get_open_exceptions(self, reference=None):
        """Get all open exceptions, optionally filtered by reference"""
        exceptions = []
        
        if os.path.exists(self.exception_file):
            with open(self.exception_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['status'] == 'Open':
                        if reference is None or row['reference'] == reference:
                            exceptions.append(row)
        
        return exceptions

    def _write_to_exception_log(self, data):
        """Write to exception log file"""
        headers = ['timestamp', 'reference', 'type', 'description', 'status', 'resolution']
        file_exists = os.path.exists(self.exception_file)
        
        with open(self.exception_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    def _write_to_audit_log(self, data):
        """Write to audit log file"""
        audit_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': data.get('action', 'Exception_Logged'),
            'reference': data.get('reference', 'N/A'),
            'details': data.get('details', 'No details provided')
        }
        
        file_exists = os.path.exists(self.audit_file)
        
        with open(self.audit_file, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=audit_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(audit_data)

    def verify_old_payment(self, data):
        """Verify old payment in both CNP and Bank Statement"""
        verification_result = {
            'cnp_verified': False,
            'bs_verified': False,
            'warnings': [],
            'requires_approval': False
        }
        
        company = data.get('company', '').upper()
        reference = data.get('reference', '')
        
        # Check CNP file
        cnp_file = os.path.join(self.base_dir, f'data/cnp/{company.lower()}/CNP_{company}.csv')
        if os.path.exists(cnp_file):
            with open(cnp_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['reference'] == reference:
                        verification_result['cnp_verified'] = True
                        break
        
        # Check Bank Statement file
        bs_file = os.path.join(self.base_dir, f'data/bank_statements/{company.lower()}/BS_{company}.csv')
        if os.path.exists(bs_file):
            with open(bs_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['reference'] == reference:
                        verification_result['bs_verified'] = True
                        break
        
        # Set warnings and approval requirements
        if not verification_result['cnp_verified']:
            verification_result['warnings'].append("Payment not found in CNP file")
            verification_result['requires_approval'] = True
        
        if not verification_result['bs_verified']:
            verification_result['warnings'].append("Payment not found in Bank Statement")
            verification_result['requires_approval'] = True
        
        if verification_result['requires_approval']:
            self.log_exception({
                'reference': reference,
                'type': 'Old_Payment_Verification',
                'description': '; '.join(verification_result['warnings'])
            })
        
        return verification_result
