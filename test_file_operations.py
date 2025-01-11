import os
import csv
from datetime import datetime
import unittest
from src.file_operations import FileOperations

class TestFileOperations(unittest.TestCase):
    def setUp(self):
        """Setup test environment"""
        self.file_ops = FileOperations()
        self.test_data = {
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary',
            'reference': 'TST-2025-0001',
            'amount': '1000.00',
            'date': '2025-01-11',
            'status': 'Pending',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def test_directory_structure(self):
        """Test if all required directories exist"""
        print("\n=== Testing Directory Structure ===")
        required_dirs = [
            'data/bank_statements/salam',
            'data/bank_statements/mvno',
            'data/cnp/salam',
            'data/cnp/mvno',
            'data/treasury'
        ]
        
        for directory in required_dirs:
            dir_path = os.path.join(self.file_ops.base_dir, directory)
            exists = os.path.exists(dir_path)
            print(f"Directory {directory}: {'EXISTS' if exists else 'MISSING'}")
            self.assertTrue(exists, f"Directory not found: {directory}")
    
    def test_file_creation(self):
        """Test file creation and headers"""
        print("\n=== Testing File Creation ===")
        files_to_test = {
            'BS-Salam': ['reference', 'amount', 'date', 'status', 'timestamp'],
            'BS-MVNO': ['reference', 'amount', 'date', 'status', 'timestamp'],
            'CNP-Salam': ['reference', 'amount', 'date', 'status', 'timestamp'],
            'CNP-MVNO': ['reference', 'amount', 'date', 'status', 'timestamp'],
            'Treasury': ['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary']
        }
        
        for file_type, expected_headers in files_to_test.items():
            file_path = self.file_ops.get_file_path(file_type)
            
            # Ensure file exists
            self.assertTrue(os.path.exists(file_path), f"File not found: {file_type}")
            print(f"File {file_type}: EXISTS")
            
            # Check headers
            with open(file_path, 'r', newline='') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                self.assertEqual(headers, expected_headers, 
                               f"Header mismatch in {file_type}")
                print(f"Headers for {file_type}: VERIFIED")
    
    def test_payment_verification(self):
        """Test payment verification functionality"""
        print("\n=== Testing Payment Verification ===")
        
        # Test new payment
        result = self.file_ops.verify_payment(self.test_data)
        self.assertFalse(result['matches'], 
                        "New payment should not match existing records")
        print("New payment verification: PASSED")
        
        # Add test payment
        self.file_ops.save_payment(self.test_data)
        print("Test payment saved")
        
        # Test duplicate payment
        result = self.file_ops.verify_payment(self.test_data)
        self.assertTrue(result['matches'], 
                       "Duplicate payment should be detected")
        print("Duplicate payment detection: PASSED")
    
    def test_payment_processing(self):
        """Test payment processing and file updates"""
        print("\n=== Testing Payment Processing ===")
        
        # Process new payment
        new_payment = self.test_data.copy()
        new_payment['reference'] = 'TST-2025-0002'
        
        # Save payment
        self.file_ops.save_payment(new_payment)
        print("Payment saved")
        
        # Verify in all files
        files_to_check = ['BS-Salam', 'CNP-Salam', 'Treasury']
        for file_type in files_to_check:
            file_path = self.file_ops.get_file_path(file_type)
            found = False
            
            with open(file_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['reference'] == new_payment['reference']:
                        found = True
                        break
            
            self.assertTrue(found, f"Payment not found in {file_type}")
            print(f"Payment verified in {file_type}")
    
    def test_file_access(self):
        """Test file access and permissions"""
        print("\n=== Testing File Access ===")
        
        for file_type in self.file_ops.file_paths.keys():
            file_path = self.file_ops.get_file_path(file_type)
            
            # Test read access
            try:
                with open(file_path, 'r') as f:
                    f.read()
                print(f"{file_type}: READ OK")
            except Exception as e:
                self.fail(f"Cannot read {file_type}: {str(e)}")
            
            # Test write access
            try:
                with open(file_path, 'a') as f:
                    f.write('')
                print(f"{file_type}: WRITE OK")
            except Exception as e:
                self.fail(f"Cannot write to {file_type}: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling in file operations"""
        print("\n=== Testing Error Handling ===")
        
        # Test invalid file type
        with self.assertRaises(ValueError):
            self.file_ops.get_file_path('INVALID')
        print("Invalid file type handling: PASSED")
        
        # Test invalid payment data (missing reference)
        invalid_data = self.test_data.copy()
        del invalid_data['reference']
        with self.assertRaises(ValueError) as cm:
            self.file_ops.save_payment(invalid_data)
        self.assertIn("Missing required field: reference", str(cm.exception))
        print("Missing field handling: PASSED")
        
        # Test invalid status
        invalid_status = self.test_data.copy()
        invalid_status['status'] = 'INVALID'
        with self.assertRaises(ValueError) as cm:
            self.file_ops.save_payment(invalid_status)
        self.assertIn("Invalid status", str(cm.exception))
        print("Invalid status handling: PASSED")

    def test_concurrent_access(self):
        """Test concurrent file access"""
        print("\n=== Testing Concurrent Access ===")
        
        import threading
        import time
        
        def save_payment(reference):
            payment = self.test_data.copy()
            payment['reference'] = reference
            try:
                self.file_ops.save_payment(payment)
                return True
            except Exception as e:
                print(f"Error in thread {reference}: {str(e)}")
                return False
        
        # Create multiple threads to save payments concurrently
        threads = []
        for i in range(5):
            ref = f'TST-2025-CONC-{i}'
            thread = threading.Thread(target=save_payment, args=(ref,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
            time.sleep(0.1)  # Small delay to ensure ordered execution
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all payments were saved
        for i in range(5):
            ref = f'TST-2025-CONC-{i}'
            verify_data = self.test_data.copy()
            verify_data['reference'] = ref
            result = self.file_ops.verify_payment(verify_data)
            self.assertTrue(result['matches'], 
                          f"Concurrent payment {ref} not saved properly")
        print("Concurrent access handling: PASSED")
    
    def test_file_locking(self):
        """Test file locking mechanism"""
        print("\n=== Testing File Locking ===")
        
        # Test lock file creation
        test_payment = self.test_data.copy()
        test_payment['reference'] = 'TST-2025-0003'
        
        # Save payment (this should create lock files)
        self.file_ops.save_payment(test_payment)
        
        # Verify lock files are cleaned up
        for file_type in ['BS-Salam', 'CNP-Salam', 'Treasury']:
            lock_path = self.file_ops.get_file_path(file_type) + '.lock'
            self.assertFalse(os.path.exists(lock_path), 
                           f"Lock file not cleaned up: {lock_path}")
        print("Lock file cleanup: PASSED")
        
    def test_corrupted_file_recovery(self):
        """Test recovery from corrupted files"""
        print("\n=== Testing Corrupted File Recovery ===")
        
        # Corrupt a test file
        file_path = self.file_ops.get_file_path('BS-Salam')
        with open(file_path, 'a', newline='') as f:
            f.write('corrupted,data,row\n')
        print("File corrupted for testing")
        
        # Try to save payment (should handle corruption)
        test_payment = self.test_data.copy()
        test_payment['reference'] = 'TST-2025-0004'
        self.file_ops.save_payment(test_payment)
        
        # Verify file was recovered
        with open(file_path, 'r', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            expected_headers = ['reference', 'amount', 'date', 'status', 'timestamp']
            self.assertEqual(headers, expected_headers,
                           "File not properly recovered")
        print("Corrupted file recovery: PASSED")
        
    def test_unicode_handling(self):
        """Test handling of Unicode characters in data"""
        print("\n=== Testing Unicode Handling ===")
        
        # Test with various Unicode characters
        unicode_data = self.test_data.copy()
        unicode_data.update({
            'reference': 'TST-2025-0005',
            'beneficiary': 'Bénéficiaire テスト 测试',
        })
        
        # Save and verify
        self.file_ops.save_payment(unicode_data)
        result = self.file_ops.verify_payment(unicode_data)
        self.assertTrue(result['matches'], 
                       "Unicode data not handled properly")
        print("Unicode handling: PASSED")
    
    def tearDown(self):
        """Clean up test data"""
        # Remove test payments
        for file_type in self.file_ops.file_paths.keys():
            file_path = self.file_ops.get_file_path(file_type)
            temp_file = file_path + '.tmp'
            
            with open(file_path, 'r', newline='') as f_in, \
                 open(temp_file, 'w', newline='') as f_out:
                reader = csv.DictReader(f_in)
                writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
                writer.writeheader()
                
                for row in reader:
                    if not row['reference'].startswith('TST-'):
                        writer.writerow(row)
            
            os.replace(temp_file, file_path)

def main():
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFileOperations)
    
    # Run tests
    print("=== Starting File Operations Tests ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
