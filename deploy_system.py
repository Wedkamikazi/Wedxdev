import os
import csv
import shutil
from datetime import datetime

class SystemDeployer:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.directories = {
            'bank_statements': {
                'salam': ['BS_SALAM_CURRENT.csv'],
                'mvno': ['BS_MVNO_CURRENT.csv']
            },
            'cnp': {
                'salam': ['CNP_SALAM_CURRENT.csv'],
                'mvno': ['CNP_MVNO_CURRENT.csv']
            },
            'treasury': ['TREASURY_CURRENT.csv'],
            'exceptions': ['EXCEPTION_LOG.csv', 'AUDIT_LOG.csv'],
            'logs': ['system.log']
        }
        
        self.file_templates = {
            'bank_statement': ['reference', 'amount', 'date', 'status', 'timestamp'],
            'cnp': ['reference', 'amount', 'date', 'status', 'timestamp'],
            'treasury': ['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary'],
            'exception': ['timestamp', 'reference_number', 'exception_type', 'description', 'status', 'resolution', 'resolved_by', 'resolved_date'],
            'audit': ['timestamp', 'action', 'reference', 'details', 'user', 'status']
        }

    def create_directory_structure(self):
        """Create the required directory structure"""
        print("\n=== Creating Directory Structure ===")
        try:
            # Create data directory
            data_dir = os.path.join(self.base_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Create subdirectories
            for main_dir, sub_dirs in self.directories.items():
                if isinstance(sub_dirs, dict):
                    # Directory has subdirectories
                    for sub_dir, files in sub_dirs.items():
                        dir_path = os.path.join(data_dir, main_dir, sub_dir)
                        os.makedirs(dir_path, exist_ok=True)
                        print(f"Created directory: {dir_path}")
                        self.create_file_templates(dir_path, files)
                else:
                    # Directory only has files
                    dir_path = os.path.join(data_dir, main_dir)
                    os.makedirs(dir_path, exist_ok=True)
                    print(f"Created directory: {dir_path}")
                    self.create_file_templates(dir_path, sub_dirs)
            
            return True
        except Exception as e:
            print(f"Error creating directory structure: {str(e)}")
            return False

    def create_file_templates(self, directory, files):
        """Create file templates with headers"""
        try:
            for file in files:
                file_path = os.path.join(directory, file)
                if not os.path.exists(file_path):
                    # Determine file type and get headers
                    if 'BS_' in file:
                        headers = self.file_templates['bank_statement']
                    elif 'CNP_' in file:
                        headers = self.file_templates['cnp']
                    elif 'TREASURY' in file:
                        headers = self.file_templates['treasury']
                    elif 'EXCEPTION' in file:
                        headers = self.file_templates['exception']
                    elif 'AUDIT' in file:
                        headers = self.file_templates['audit']
                    else:
                        headers = []

                    # Create file with headers
                    with open(file_path, 'w', newline='') as f:
                        writer = csv.writer(f)
                        if headers:
                            writer.writerow(headers)
                    print(f"Created file template: {file_path}")
            
            return True
        except Exception as e:
            print(f"Error creating file templates: {str(e)}")
            return False

    def verify_deployment(self):
        """Verify the deployment was successful"""
        print("\n=== Verifying Deployment ===")
        try:
            # Check directories
            for main_dir, sub_dirs in self.directories.items():
                if isinstance(sub_dirs, dict):
                    for sub_dir, files in sub_dirs.items():
                        dir_path = os.path.join(self.base_dir, 'data', main_dir, sub_dir)
                        if not os.path.exists(dir_path):
                            print(f"ERROR: Missing directory: {dir_path}")
                            return False
                        for file in files:
                            file_path = os.path.join(dir_path, file)
                            if not os.path.exists(file_path):
                                print(f"ERROR: Missing file: {file_path}")
                                return False
                else:
                    dir_path = os.path.join(self.base_dir, 'data', main_dir)
                    if not os.path.exists(dir_path):
                        print(f"ERROR: Missing directory: {dir_path}")
                        return False
                    for file in sub_dirs:
                        file_path = os.path.join(dir_path, file)
                        if not os.path.exists(file_path):
                            print(f"ERROR: Missing file: {file_path}")
                            return False
            
            print("SUCCESS: All directories and files verified successfully")
            return True
        except Exception as e:
            print(f"ERROR: Error verifying deployment: {str(e)}")
            return False

    def deploy(self):
        """Run the full deployment process"""
        print("=== Starting Payment System Deployment ===")
        print(f"Base Directory: {self.base_dir}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Create Directory Structure
        if not self.create_directory_structure():
            print("ERROR: Failed to create directory structure")
            return False
            
        # Step 2: Verify Deployment
        if not self.verify_deployment():
            print("ERROR: Deployment verification failed")
            return False
            
        print("\nSUCCESS: Deployment completed successfully!")
        return True

def main():
    # Get the directory where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create deployer
    deployer = SystemDeployer(base_dir)
    
    # Run deployment
    if deployer.deploy():
        print("\nSystem is ready for operation!")
    else:
        print("\nDeployment failed. Please check the errors above.")

if __name__ == "__main__":
    main()
