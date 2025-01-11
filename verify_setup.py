import os
import csv
import sys
from datetime import datetime

class SystemVerifier:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.src_dir = os.path.join(self.base_dir, 'src')
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.verification_results = []
        
        # Add src directory to Python path
        if self.src_dir not in sys.path:
            sys.path.append(self.src_dir)
        
    def log_result(self, component, status, message):
        """Log verification result"""
        result = {
            'component': component,
            'status': status,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.verification_results.append(result)
        status_symbol = "PASS" if status else "FAIL"
        print(f"[{status_symbol}] {component}: {message}")
        
    def verify_directory_structure(self):
        """Verify all required directories exist"""
        print("\n=== Verifying Directory Structure ===")
        
        required_dirs = {
            'src': self.src_dir,
            'data': self.data_dir,
            'bank_statements/salam': os.path.join(self.data_dir, 'bank_statements', 'salam'),
            'bank_statements/mvno': os.path.join(self.data_dir, 'bank_statements', 'mvno'),
            'cnp/salam': os.path.join(self.data_dir, 'cnp', 'salam'),
            'cnp/mvno': os.path.join(self.data_dir, 'cnp', 'mvno'),
            'treasury': os.path.join(self.data_dir, 'treasury'),
            'exceptions': os.path.join(self.data_dir, 'exceptions'),
            'logs': os.path.join(self.data_dir, 'logs')
        }
        
        for dir_name, dir_path in required_dirs.items():
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                self.log_result(f"Directory: {dir_name}", True, f"Found at {dir_path}")
            else:
                self.log_result(f"Directory: {dir_name}", False, f"Not found at {dir_path}")
    
    def verify_system_files(self):
        """Verify all required system files exist"""
        print("\n=== Verifying System Files ===")
        
        required_files = {
            'payment_system.py': {'path': 'src', 'required': True},
            'validation_system.py': {'path': 'src', 'required': True},
            'file_operations.py': {'path': 'src', 'required': True},
            'status_tracker.py': {'path': 'src', 'required': True},
            'exception_handler.py': {'path': 'src', 'required': True},
            'audit_trail.py': {'path': 'src', 'required': True},
            '__init__.py': {'path': 'src', 'required': True}
        }
        
        for file_name, config in required_files.items():
            file_path = os.path.join(self.base_dir, config['path'], file_name)
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                self.log_result(f"File: {file_name}", True, "Present and not empty")
            else:
                self.log_result(f"File: {file_name}", False, "Missing or empty")
    
    def verify_csv_files(self):
        """Verify CSV files exist and have correct headers"""
        print("\n=== Verifying CSV Files ===")
        
        csv_files = {
            'BS_SALAM_CURRENT.csv': {
                'path': os.path.join('data', 'bank_statements', 'salam'),
                'headers': ['reference', 'amount', 'date', 'status', 'timestamp']
            },
            'BS_MVNO_CURRENT.csv': {
                'path': os.path.join('data', 'bank_statements', 'mvno'),
                'headers': ['reference', 'amount', 'date', 'status', 'timestamp']
            },
            'CNP_SALAM_CURRENT.csv': {
                'path': os.path.join('data', 'cnp', 'salam'),
                'headers': ['reference', 'amount', 'date', 'status', 'timestamp']
            },
            'CNP_MVNO_CURRENT.csv': {
                'path': os.path.join('data', 'cnp', 'mvno'),
                'headers': ['reference', 'amount', 'date', 'status', 'timestamp']
            },
            'TREASURY_CURRENT.csv': {
                'path': os.path.join('data', 'treasury'),
                'headers': ['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary']
            },
            'EXCEPTION_LOG.csv': {
                'path': os.path.join('data', 'exceptions'),
                'headers': ['timestamp', 'reference_number', 'exception_type', 'description', 'status', 'resolution', 'resolved_by', 'resolved_date']
            },
            'AUDIT_LOG.csv': {
                'path': os.path.join('data', 'exceptions'),
                'headers': ['timestamp', 'action', 'reference', 'details', 'user', 'status']
            }
        }
        
        for file_name, config in csv_files.items():
            file_path = os.path.join(self.base_dir, config['path'], file_name)
            if not os.path.exists(file_path):
                self.log_result(f"CSV: {file_name}", False, "File not found")
                continue
                
            try:
                with open(file_path, 'r', newline='') as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    if headers == config['headers']:
                        self.log_result(f"CSV: {file_name}", True, "Headers verified")
                    else:
                        self.log_result(f"CSV: {file_name}", False, 
                                      f"Header mismatch. Expected: {config['headers']}, Got: {headers}")
            except Exception as e:
                self.log_result(f"CSV: {file_name}", False, f"Error reading file: {str(e)}")
    
    def verify_python_path(self):
        """Verify src directory is in Python path"""
        print("\n=== Verifying Python Path ===")
        
        if self.src_dir in sys.path:
            self.log_result("Python Path", True, "src directory found in Python path")
        else:
            self.log_result("Python Path", False, "src directory not found in Python path")
    
    def verify_logging(self):
        """Verify logging system"""
        print("\n=== Verifying Logging System ===")
        
        log_file = os.path.join(self.data_dir, 'logs', 'system.log')
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    if content and "System Initialized" in content:
                        self.log_result("Logging", True, "Log file initialized and contains entries")
                    else:
                        self.log_result("Logging", False, "Log file empty or missing initialization entry")
            except Exception as e:
                self.log_result("Logging", False, f"Error reading log file: {str(e)}")
        else:
            self.log_result("Logging", False, "Log file not found")
    
    def verify_all(self):
        """Run all verifications"""
        print("=== Starting System Verification ===")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base Directory: {self.base_dir}")
        
        # Run all verifications
        self.verify_directory_structure()
        self.verify_system_files()
        self.verify_csv_files()
        self.verify_python_path()
        self.verify_logging()
        
        # Print summary
        print("\n=== Verification Summary ===")
        total = len(self.verification_results)
        passed = sum(1 for r in self.verification_results if r['status'])
        failed = total - passed
        
        print(f"Total Checks: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed > 0:
            print("\nFailed Checks:")
            for result in self.verification_results:
                if not result['status']:
                    print(f"- {result['component']}: {result['message']}")
        
        return failed == 0

def main():
    verifier = SystemVerifier()
    if verifier.verify_all():
        print("\nSystem verification completed successfully!")
    else:
        print("\nSystem verification failed! Please check the errors above.")

if __name__ == "__main__":
    main()
