import os
import csv
from datetime import datetime
import sys

class SystemInitializer:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.src_dir = os.path.join(self.base_dir, 'src')
        
        # Add src directory to Python path
        if self.src_dir not in sys.path:
            sys.path.append(self.src_dir)
    
    def initialize_csv_files(self):
        """Initialize CSV files with headers"""
        print("\n=== Initializing CSV Files ===")
        
        # Define file templates
        templates = {
            'bank_statement': {
                'headers': ['reference', 'amount', 'date', 'status', 'timestamp'],
                'files': [
                    'data/bank_statements/salam/BS_SALAM_CURRENT.csv',
                    'data/bank_statements/mvno/BS_MVNO_CURRENT.csv'
                ]
            },
            'cnp': {
                'headers': ['reference', 'amount', 'date', 'status', 'timestamp'],
                'files': [
                    'data/cnp/salam/CNP_SALAM_CURRENT.csv',
                    'data/cnp/mvno/CNP_MVNO_CURRENT.csv'
                ]
            },
            'treasury': {
                'headers': ['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary'],
                'files': ['data/treasury/TREASURY_CURRENT.csv']
            },
            'exception': {
                'headers': ['timestamp', 'reference', 'type', 'description', 'status', 'resolution'],
                'files': ['data/exceptions/EXCEPTION_LOG.csv']
            },
            'audit': {
                'headers': ['timestamp', 'action', 'reference', 'details', 'status'],
                'files': ['data/exceptions/AUDIT_LOG.csv']
            }
        }
        
        try:
            for template_type, config in templates.items():
                for file_path in config['files']:
                    full_path = os.path.join(self.base_dir, file_path)
                    if not os.path.exists(os.path.dirname(full_path)):
                        os.makedirs(os.path.dirname(full_path))
                    
                    # Initialize file with headers if empty or doesn't exist
                    if not os.path.exists(full_path) or os.path.getsize(full_path) == 0:
                        with open(full_path, 'w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(config['headers'])
                        print(f"SUCCESS: Initialized {os.path.basename(file_path)}")
                    else:
                        print(f"INFO: {os.path.basename(file_path)} already initialized")
            
            return True
        except Exception as e:
            print(f"ERROR: Failed to initialize CSV files: {str(e)}")
            return False
    
    def initialize_logging(self):
        """Initialize system logging"""
        print("\n=== Initializing System Logging ===")
        
        try:
            log_file = os.path.join(self.data_dir, 'logs', 'system.log')
            
            # Create logs directory if it doesn't exist
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Initialize log file with header
            with open(log_file, 'a') as f:
                f.write(f"\n=== System Initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            
            print(f"SUCCESS: Initialized system logging at {log_file}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to initialize logging: {str(e)}")
            return False
    
    def verify_system_files(self):
        """Verify all required system files are present"""
        print("\n=== Verifying System Files ===")
        
        required_files = [
            'payment_system.py',
            'validation_system.py',
            'file_operations.py',
            'status_tracker.py',
            'exception_handler.py',
            'audit_trail.py'
        ]
        
        try:
            missing_files = []
            for file in required_files:
                file_path = os.path.join(self.src_dir, file)
                if not os.path.exists(file_path):
                    missing_files.append(file)
            
            if missing_files:
                print("ERROR: Missing required files:")
                for file in missing_files:
                    print(f"  - {file}")
                return False
            
            print("SUCCESS: All system files verified")
            return True
        except Exception as e:
            print(f"ERROR: Failed to verify system files: {str(e)}")
            return False
    
    def initialize(self):
        """Run complete system initialization"""
        print("=== Starting System Initialization ===")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base Directory: {self.base_dir}")
        
        # Step 1: Verify system files
        if not self.verify_system_files():
            return False
        
        # Step 2: Initialize CSV files
        if not self.initialize_csv_files():
            return False
        
        # Step 3: Initialize logging
        if not self.initialize_logging():
            return False
        
        print("\nSUCCESS: System initialization completed!")
        return True

def main():
    initializer = SystemInitializer()
    if initializer.initialize():
        print("\nSystem is ready to start!")
    else:
        print("\nSystem initialization failed!")

if __name__ == "__main__":
    main()
