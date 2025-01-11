import unittest
from datetime import datetime
import os
import csv
from exception_handler import ExceptionHandler

class TestExceptionHandler(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.handler = ExceptionHandler()
        self.test_reference = "TEST-2025-0001"
        self.test_data = {
            'reference': 'TST-2025-0001',
            'company': 'SALAM',
            'amount': '1000.00',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'Under Process'
        }
        
        # Instead of removing, just ensure the file is empty
        if os.path.exists(self.handler.audit_file):
            with open(self.handler.audit_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'action', 'reference', 'details'])
        if os.path.exists(self.handler.exception_file):
            with open(self.handler.exception_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'reference', 'type', 'description', 'status', 'resolution'])
        
        # Ensure test directories exist
        os.makedirs(os.path.dirname(self.handler.exception_file), exist_ok=True)
        os.makedirs(os.path.join(self.handler.base_dir, 'data/cnp/salam'), exist_ok=True)
        os.makedirs(os.path.join(self.handler.base_dir, 'data/bank_statements/salam'), exist_ok=True)
        
        # Create test files
        self._create_test_files()

    def _create_test_files(self):
        """Create test files with sample data"""
        # Create CNP test file
        cnp_file = os.path.join(self.handler.base_dir, 'data/cnp/salam/CNP_SALAM.csv')
        with open(cnp_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['reference', 'amount', 'date', 'status', 'timestamp'])
            writer.writerow(['TST-2025-0001', '1000.00', '2025-01-01', 'Completed', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        
        # Create Bank Statement test file
        bs_file = os.path.join(self.handler.base_dir, 'data/bank_statements/salam/BS_SALAM.csv')
        with open(bs_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['reference', 'amount', 'date', 'status', 'timestamp'])
            writer.writerow(['TST-2025-0001', '1000.00', '2025-01-01', 'Completed', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

    def test_1_log_exception_basic(self):
        """Test basic exception logging"""
        data = {
            'reference': self.test_reference,
            'type': 'TEST_ERROR',
            'description': 'Test error description'
        }
        result = self.handler.log_exception(data)
        self.assertIsNotNone(result)
        self.assertEqual(result['reference'], self.test_reference)
        self.assertEqual(result['status'], 'Open')
        
    def test_2_log_exception_empty_reference(self):
        """Test exception logging with empty reference"""
        data = {
            'reference': '',
            'type': 'TEST_ERROR',
            'description': 'Test error description'
        }
        result = self.handler.log_exception(data)
        self.assertEqual(result['reference'], 'N/A')
        
    def test_3_log_exception_special_chars(self):
        """Test exception logging with special characters"""
        data = {
            'reference': 'TEST-2025-SP#@!',
            'type': 'TEST_ERROR_$%^',
            'description': 'Test error description with @#$%^&*'
        }
        result = self.handler.log_exception(data)
        self.assertIsNotNone(result)
        
    def test_4_resolve_exception_valid(self):
        """Test resolving a valid exception"""
        # First create an exception
        data = {
            'reference': self.test_reference,
            'type': 'TEST_ERROR',
            'description': 'Test error description'
        }
        self.handler.log_exception(data)
        
        # Now resolve it
        resolution_data = {
            'resolution': 'Test resolution',
            'resolved_by': 'Test User'
        }
        result = self.handler.resolve_exception(self.test_reference, resolution_data)
        self.assertTrue(result)
        
    def test_5_resolve_exception_nonexistent(self):
        """Test resolving a non-existent exception"""
        resolution_data = {
            'resolution': 'Test resolution',
            'resolved_by': 'Test User'
        }
        result = self.handler.resolve_exception('NONEXISTENT-REF', resolution_data)
        self.assertFalse(result)
        
    def test_6_resolve_exception_already_resolved(self):
        """Test resolving an already resolved exception"""
        # Create and resolve an exception
        data = {
            'reference': 'TEST-RESOLVED',
            'type': 'TEST_ERROR',
            'description': 'Test error description'
        }
        self.handler.log_exception(data)
        resolution_data = {
            'resolution': 'First resolution',
            'resolved_by': 'Test User'
        }
        self.handler.resolve_exception('TEST-RESOLVED', resolution_data)
        
        # Try to resolve it again
        resolution_data['resolution'] = 'Second resolution'
        result = self.handler.resolve_exception('TEST-RESOLVED', resolution_data)
        self.assertFalse(result)
        
    def test_7_get_open_exceptions_basic(self):
        """Test getting open exceptions"""
        # Create some test exceptions
        for i in range(3):
            data = {
                'reference': f'TEST-OPEN-{i}',
                'type': 'TEST_ERROR',
                'description': f'Test error description {i}'
            }
            self.handler.log_exception(data)
            
        exceptions = self.handler.get_open_exceptions()
        self.assertGreaterEqual(len(exceptions), 3)
        
    def test_8_get_open_exceptions_filtered(self):
        """Test getting open exceptions filtered by reference"""
        # Create a specific test exception
        data = {
            'reference': 'TEST-FILTER',
            'type': 'TEST_ERROR',
            'description': 'Test error description'
        }
        self.handler.log_exception(data)
        
        exceptions = self.handler.get_open_exceptions('TEST-FILTER')
        self.assertEqual(len(exceptions), 1)
        self.assertEqual(exceptions[0]['reference'], 'TEST-FILTER')
        
    def test_9_exception_file_creation(self):
        """Test exception file creation and headers"""
        # Create a test exception to generate the file
        data = {
            'reference': 'TEST-FILE',
            'type': 'TEST_ERROR',
            'description': 'Test error description'
        }
        self.handler.log_exception(data)
        
        file_path = self.handler.exception_file
        self.assertTrue(os.path.exists(file_path))
        
        with open(file_path, 'r', newline='') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            expected_headers = ['timestamp', 'reference', 'type', 
                              'description', 'status', 'resolution']
            self.assertEqual(set(headers), set(expected_headers))
            
    def test_10_concurrent_exceptions(self):
        """Test logging multiple exceptions rapidly"""
        exceptions = []
        for i in range(100):
            data = {
                'reference': f'TEST-CONCURRENT-{i}',
                'type': 'TEST_ERROR',
                'description': f'Test error description {i}'
            }
            result = self.handler.log_exception(data)
            exceptions.append(result)
            
        self.assertEqual(len(exceptions), 100)
        
    def test_11_large_description(self):
        """Test handling very large description text"""
        large_text = 'A' * 10000  # 10KB of text
        data = {
            'reference': 'TEST-LARGE',
            'type': 'TEST_ERROR',
            'description': large_text
        }
        result = self.handler.log_exception(data)
        self.assertIsNotNone(result)
        
    def test_12_malformed_data(self):
        """Test handling malformed data"""
        malformed_data = [
            {},  # Empty dict
            {'reference': None, 'type': None, 'description': None},  # None values
            {'reference': '', 'type': '', 'description': ''},  # Empty strings
            {'reference': 123, 'type': 456, 'description': 789},  # Wrong types
        ]
        
        for data in malformed_data:
            result = self.handler.log_exception(data)
            self.assertIsNotNone(result)

    def test_13_verify_old_payment_both_exist(self):
        """Test verification when payment exists in both CNP and Bank Statement"""
        result = self.handler.verify_old_payment(self.test_data)
        self.assertTrue(result['cnp_verified'])
        self.assertTrue(result['bs_verified'])
        self.assertFalse(result['requires_approval'])
        self.assertEqual(len(result['warnings']), 0)

    def test_14_verify_old_payment_missing_cnp(self):
        """Test verification when payment is missing from CNP"""
        test_data = self.test_data.copy()
        test_data['reference'] = 'TST-2025-0002'
        
        result = self.handler.verify_old_payment(test_data)
        self.assertFalse(result['cnp_verified'])
        self.assertFalse(result['bs_verified'])
        self.assertTrue(result['requires_approval'])
        self.assertIn("Payment not found in CNP file", result['warnings'])

    def test_15_verify_old_payment_missing_bs(self):
        """Test verification when payment is missing from Bank Statement"""
        # Add to CNP only
        cnp_file = os.path.join(self.handler.base_dir, 'data/cnp/salam/CNP_SALAM.csv')
        with open(cnp_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['TST-2025-0003', '1000.00', '2025-01-01', 'Completed', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        
        test_data = self.test_data.copy()
        test_data['reference'] = 'TST-2025-0003'
        
        result = self.handler.verify_old_payment(test_data)
        self.assertTrue(result['cnp_verified'])
        self.assertFalse(result['bs_verified'])
        self.assertTrue(result['requires_approval'])
        self.assertIn("Payment not found in Bank Statement", result['warnings'])

    def test_16_verify_old_payment_missing_both(self):
        """Test verification when payment is missing from both CNP and Bank Statement"""
        test_data = self.test_data.copy()
        test_data['reference'] = 'TST-2025-0004'
        
        result = self.handler.verify_old_payment(test_data)
        self.assertFalse(result['cnp_verified'])
        self.assertFalse(result['bs_verified'])
        self.assertTrue(result['requires_approval'])
        self.assertEqual(len(result['warnings']), 2)
        self.assertIn("Payment not found in CNP file", result['warnings'])
        self.assertIn("Payment not found in Bank Statement", result['warnings'])

    def test_17_verify_old_payment_invalid_company(self):
        """Test verification with invalid company"""
        test_data = self.test_data.copy()
        test_data['company'] = 'INVALID'
        
        result = self.handler.verify_old_payment(test_data)
        self.assertFalse(result['cnp_verified'])
        self.assertFalse(result['bs_verified'])
        self.assertTrue(result['requires_approval'])

    def tearDown(self):
        """Clean up test files"""
        files_to_cleanup = [
            os.path.join(self.handler.base_dir, 'data/cnp/salam/CNP_SALAM.csv'),
            os.path.join(self.handler.base_dir, 'data/bank_statements/salam/BS_SALAM.csv'),
            self.handler.exception_file,
            self.handler.audit_file
        ]
        
        for file in files_to_cleanup:
            if os.path.exists(file):
                os.remove(file)

if __name__ == '__main__':
    unittest.main()
