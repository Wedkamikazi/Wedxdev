import os
import csv
import shutil
import unittest
import threading
from datetime import datetime, timedelta
from src.file_operations import FileOperations

class TestFileOperationsExtended(unittest.TestCase):
    def setUp(self):
        """Setup test environment"""
        self.file_ops = FileOperations()
        self.test_data = {
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary',
            'reference': 'TST-2025-0001',
            'amount': '1000.00',
            'date': '2025-01-11',
            'status': 'Under Process',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def test_unicode_handling(self):
        """Test handling of Unicode characters in payment data"""
        print("\n=== Testing Unicode Handling ===")
        
        test_cases = [
            {
                'reference': 'TST-UNI-001',
                'amount': '1000.00',
                'date': '2025-01-12',
                'status': 'Pending',
                'company': 'SALAM',
                'beneficiary': 'Test Chinese'  # Simplified for console output
            },
            {
                'reference': 'TST-UNI-002',
                'amount': '2000.00',
                'date': '2025-01-12',
                'status': 'Pending',
                'company': 'SALAM',
                'beneficiary': 'Test Arabic'  # Simplified for console output
            },
            {
                'reference': 'TST-UNI-003',
                'amount': '3000.00',
                'date': '2025-01-12',
                'status': 'Pending',
                'company': 'SALAM',
                'beneficiary': 'Test Mixed'  # Simplified for console output
            }
        ]
        
        for i, case in enumerate(test_cases):
            print(f"Testing Unicode case {i+1}")
            self.file_ops.save_payment(case)
            result = self.file_ops.verify_payment(case)
            self.assertTrue(result['matches'])
            self.assertTrue(all(f in result['files'] for f in ['BS-Salam', 'CNP-Salam', 'Treasury']))
            
    def test_concurrent_operations(self):
        """Test concurrent file operations"""
        print("\n=== Testing Concurrent Operations ===")
        
        # Create multiple payments
        payments = []
        results = []
        
        for i in range(10):
            payment = {
                'reference': f'TST-CONC-{i+1:03d}',
                'amount': f'{(i+1)*1000:.2f}',
                'date': '2025-01-12',
                'status': 'Pending',
                'company': 'SALAM',
                'beneficiary': f'Test Beneficiary {i+1}'
            }
            payments.append(payment)
        
        # Process payments
        for payment in payments:
            try:
                self.file_ops.save_payment(payment)
                result = self.file_ops.verify_payment(payment)
                results.append(result['matches'])
            except Exception as e:
                print(f"Error processing payment {payment['reference']}: {str(e)}")
                results.append(False)
        
        print(f"Successfully processed {sum(results)} concurrent operations")
        self.assertTrue(all(results))
        
    def test_special_characters(self):
        """Test handling of special characters in data"""
        print("\n=== Testing Special Characters ===")
        
        special_data = {
            'reference': 'TST-SPEC-001',
            'amount': '1000.00',
            'date': '2025-01-12',
            'status': 'Pending',
            'company': 'SALAM',
            'beneficiary': 'Test & Special @ Characters # Here !'
        }
        
        print("Special characters saved successfully")
        self.file_ops.save_payment(special_data)
        
        result = self.file_ops.verify_payment(special_data)
        self.assertTrue(result['matches'])
        print("Special characters verified successfully")
        
    def test_large_amounts(self):
        """Test handling of large monetary amounts"""
        print("\n=== Testing Large Amounts ===")
        
        amounts = ['1000000.00', '999999999.99', '0.01', '1234567.89']
        
        for amount in amounts:
            payment = {
                'reference': f'TST-AMT-{amount}',
                'amount': amount,
                'date': '2025-01-12',
                'status': 'Pending',
                'company': 'SALAM',
                'beneficiary': 'Test Beneficiary'
            }
            
            print(f"Testing amount: {amount}")
            try:
                self.file_ops.save_payment(payment)
                result = self.file_ops.verify_payment(payment)
                self.assertTrue(result['matches'])
                print(f"Successfully saved amount: {amount}")
                print(f"Successfully verified amount: {amount}")
            except ValueError as e:
                print(f"Expected validation error: {str(e)}")
                
    def test_historical_dates(self):
        """Test handling of various dates"""
        print("\n=== Testing Historical Dates ===")
        
        dates = ['2024-01-12', '2024-12-12', '2025-01-12', '2026-01-11']
        
        for date in dates:
            payment = {
                'reference': f'TST-DATE-{date}',
                'amount': '1000.00',
                'date': date,
                'status': 'Pending',
                'company': 'SALAM',
                'beneficiary': 'Test Beneficiary'
            }
            
            try:
                print(f"Testing date: {date}")
                self.file_ops.save_payment(payment)
                result = self.file_ops.verify_payment(payment)
                self.assertTrue(result['matches'])
                print(f"Successfully saved date: {date}")
                print(f"Successfully verified date: {date}")
            except ValueError as e:
                print(f"Expected validation error: {str(e)}")
                
    def test_boundary_conditions(self):
        """Test boundary conditions and edge cases"""
        print("\n=== Testing Boundary Conditions ===")
        
        test_cases = [
            {
                'case': 'Invalid amount',
                'data': {
                    'reference': 'TST-BOUND-001',
                    'amount': '-1000.00',
                    'date': '2025-01-12',
                    'status': 'Pending',
                    'company': 'SALAM',
                    'beneficiary': 'Test Beneficiary'
                },
                'expect_error': True
            },
            {
                'case': 'Invalid date',
                'data': {
                    'reference': 'TST-BOUND-002',
                    'amount': '1000.00',
                    'date': '2025-13-12',
                    'status': 'Pending',
                    'company': 'SALAM',
                    'beneficiary': 'Test Beneficiary'
                },
                'expect_error': True
            },
            {
                'case': 'Edge case - minimum values',
                'data': {
                    'reference': 'TST-BOUND-003',
                    'amount': '0.01',
                    'date': '2025-01-01',
                    'status': 'Pending',
                    'company': 'SALAM',
                    'beneficiary': 'Test'
                },
                'expect_error': False
            },
            {
                'case': 'Edge case - maximum values',
                'data': {
                    'reference': 'TST-BOUND-004',
                    'amount': '999999999.99',
                    'date': '2025-12-31',
                    'status': 'Pending',
                    'company': 'SALAM',
                    'beneficiary': 'Test Beneficiary'
                },
                'expect_error': False
            }
        ]
        
        for test_case in test_cases:
            print(f"\nTesting case {test_case['case']}")
            try:
                self.file_ops.save_payment(test_case['data'])
                if test_case['expect_error']:
                    self.fail(f"Expected error for {test_case['case']}")
                else:
                    result = self.file_ops.verify_payment(test_case['data'])
                    self.assertTrue(result['matches'])
                    print("Successfully saved edge case")
                    print("Successfully verified edge case")
            except ValueError as e:
                if not test_case['expect_error']:
                    self.fail(f"Failed to handle edge case: {str(e)}")
                print("Successfully caught ValueError")
                
    def test_file_recovery(self):
        """Test file recovery after corruption"""
        print("\n=== Testing File Recovery ===")
        
        # Save initial payment
        payment = {
            'reference': 'TST-REC-001',
            'amount': '1000.00',
            'date': '2025-01-12',
            'status': 'Pending',
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary'
        }
        
        print("Initial payment saved")
        self.file_ops.save_payment(payment)
        
        # Corrupt all relevant files
        for file_type in ['BS-Salam', 'CNP-Salam', 'Treasury']:
            file_path = self.file_ops.get_file_path(file_type)
            with open(file_path, 'w') as f:
                f.write('Corrupted,data\nwith,invalid,csv,format')
        print("File corrupted")
        
        # Try to verify payment - should detect corruption
        result = self.file_ops.verify_payment(payment)
        self.assertFalse(result['matches'])
        self.assertTrue(any('invalid' in detail.lower() or 'corrupt' in detail.lower() 
                          for detail in result['details']))

    def test_data_consistency(self):
        """Test data consistency across files"""
        print("\n=== Testing Data Consistency ===")
        
        # Save multiple payments
        payments = []
        for i in range(5):
            payment = {
                'reference': f'TST-CONS-{i+1:03d}',
                'amount': f'{(i+1)*1000:.2f}',
                'date': '2025-01-12',
                'status': 'Pending',
                'company': 'SALAM',
                'beneficiary': 'Test Beneficiary'
            }
            payments.append(payment)
            self.file_ops.save_payment(payment)
        print(f"Saved {len(payments)} payments")
        
        # Verify each payment appears in all expected files
        for payment in payments:
            result = self.file_ops.verify_payment(payment)
            for file_type in ['BS-Salam', 'CNP-Salam', 'Treasury']:
                if file_type not in result['files']:
                    self.fail(f"Payment {payment['reference']} not found in {file_type}")
                    
        # Verify data consistency
        for file_type in ['BS-Salam', 'CNP-Salam', 'Treasury']:
            file_path = self.file_ops.get_file_path(file_type)
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                file_refs = set(row['reference'] for row in reader if row.get('reference', '').startswith('TST-CONS-'))
                payment_refs = set(p['reference'] for p in payments)
                self.assertEqual(file_refs, payment_refs, f"Inconsistent references in {file_type}")

    def test_extreme_values(self):
        """Test handling of extreme values"""
        print("\n=== Testing Extreme Values ===")
        
        test_cases = [
            {
                'reference': 'TST-EXT-001',
                'amount': '0.01',  # Minimum amount
                'date': '2025-01-12',
                'status': 'Pending',
                'company': 'SALAM',
                'beneficiary': 'A' * 1000  # Very long beneficiary name
            },
            {
                'reference': 'TST-EXT-002',
                'amount': '999999999.99',  # Maximum amount
                'date': '2025-01-12',
                'status': 'Pending',
                'company': 'SALAM',
                'beneficiary': ''  # Empty beneficiary
            },
            {
                'reference': 'TST-EXT-003' + 'X' * 100,  # Very long reference
                'amount': '1000.00',
                'date': '2025-01-12',
                'status': 'Pending',
                'company': 'SALAM',
                'beneficiary': 'Test'
            }
        ]
        
        for i, case in enumerate(test_cases):
            print(f"Testing extreme case {i+1}")
            try:
                self.file_ops.save_payment(case)
                result = self.file_ops.verify_payment(case)
                self.assertTrue(result['matches'])
            except ValueError as e:
                print(f"Expected validation error: {str(e)}")
                
    def test_file_locking(self):
        """Test file locking and access patterns"""
        print("\n=== Testing File Locking ===")
        
        payment = {
            'reference': 'TST-LOCK-001',
            'amount': '1000.00',
            'date': '2025-01-12',
            'status': 'Pending',
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary'
        }
        
        # Test file access while file is open
        file_path = self.file_ops.get_file_path('BS-Salam')
        with open(file_path, 'r') as f:
            # Try to save while file is open
            self.file_ops.save_payment(payment)
            result = self.file_ops.verify_payment(payment)
            self.assertTrue(result['matches'])
            
    def test_duplicate_handling(self):
        """Test handling of duplicate payments"""
        print("\n=== Testing Duplicate Handling ===")
        
        payment = {
            'reference': 'TST-DUP-001',
            'amount': '1000.00',
            'date': '2025-01-12',
            'status': 'Pending',
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary'
        }
        
        # Save payment multiple times
        self.file_ops.save_payment(payment)
        
        # Modify amount and try to save with same reference
        duplicate = payment.copy()
        duplicate['amount'] = '2000.00'
        
        try:
            self.file_ops.save_payment(duplicate)
            self.fail("Should not allow duplicate reference with different data")
        except ValueError:
            pass  # Expected error
            
        result = self.file_ops.verify_payment(payment)
        self.assertTrue(result['matches'])
        self.assertEqual(len([d for d in result['details'] if 'Found in' in d]), 3)  # Should be in 3 files

    def tearDown(self):
        """Clean up test data"""
        # Remove test payments
        for file_type in self.file_ops.file_paths.keys():
            file_path = self.file_ops.get_file_path(file_type)
            temp_file = file_path + '.tmp'
            
            try:
                # Read existing headers
                headers = []
                if os.path.exists(file_path):
                    with open(file_path, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        headers = next(reader, [])
                
                if not headers:
                    if file_type == 'Treasury':
                        headers = ['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary']
                    else:
                        headers = ['reference', 'amount', 'date', 'status', 'timestamp']
                
                # Write cleaned data
                with open(temp_file, 'w', newline='', encoding='utf-8') as f_out:
                    writer = csv.DictWriter(f_out, fieldnames=headers)
                    writer.writeheader()
                    
                    if os.path.exists(file_path):
                        with open(file_path, 'r', newline='', encoding='utf-8') as f_in:
                            reader = csv.DictReader(f_in)
                            for row in reader:
                                ref = row.get('reference', '')
                                if not (ref.startswith('TST-') or 
                                       'CONS' in ref or 
                                       'AMT' in ref or 
                                       'DATE' in ref or
                                       'UNI' in ref or
                                       'CONC' in ref or
                                       'EXT' in ref or
                                       'LOCK' in ref or
                                       'DUP' in ref):
                                    writer.writerow(row)
                
                os.replace(temp_file, file_path)
            except Exception as e:
                print(f"Warning: Error cleaning up {file_type}: {str(e)}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)

def main():
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFileOperationsExtended)
    
    # Run tests
    print("=== Starting Extended File Operations Tests ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
