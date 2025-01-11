import unittest
from datetime import datetime, timedelta
from validation_system import ValidationSystem
import csv
import os

class TestValidationSystem(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.validator = ValidationSystem()
        self.base_test_data = {
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary',
            'reference': 'TEST-2025-001',
            'amount': '10000.00',
            'date': datetime.now().strftime('%Y-%m-%d')
        }

    def test_1_validate_input_valid_data(self):
        """Test validation with valid input data"""
        result = self.validator.validate_input(self.base_test_data)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(len(result['warnings']), 0)

    def test_2_validate_input_missing_company(self):
        """Test validation with missing company"""
        data = self.base_test_data.copy()
        data['company'] = ''
        result = self.validator.validate_input(data)
        self.assertFalse(result['valid'])
        self.assertIn("Company selection required", result['errors'])

    def test_3_validate_input_missing_beneficiary(self):
        """Test validation with missing beneficiary"""
        data = self.base_test_data.copy()
        data['beneficiary'] = '   '
        result = self.validator.validate_input(data)
        self.assertFalse(result['valid'])
        self.assertIn("Beneficiary name required", result['errors'])

    def test_4_validate_reference_invalid_chars(self):
        """Test validation with invalid reference characters"""
        data = self.base_test_data.copy()
        data['reference'] = 'TEST@2025#001'
        result = self.validator.validate_input(data)
        self.assertFalse(result['valid'])
        self.assertIn("Invalid reference format", result['errors'])

    def test_5_validate_reference_empty(self):
        """Test validation with empty reference"""
        data = self.base_test_data.copy()
        data['reference'] = ''
        result = self.validator.validate_input(data)
        self.assertFalse(result['valid'])
        self.assertIn("Invalid reference format", result['errors'])

    def test_6_validate_amount_negative(self):
        """Test validation with negative amount"""
        data = self.base_test_data.copy()
        data['amount'] = '-1000.00'
        result = self.validator.validate_input(data)
        self.assertFalse(result['valid'])
        self.assertIn("Amount must be greater than 0", result['errors'])

    def test_7_validate_amount_zero(self):
        """Test validation with zero amount"""
        data = self.base_test_data.copy()
        data['amount'] = '0.00'
        result = self.validator.validate_input(data)
        self.assertFalse(result['valid'])
        self.assertIn("Amount must be greater than 0", result['errors'])

    def test_8_validate_amount_exceeds_limit(self):
        """Test validation with amount exceeding limit"""
        data = self.base_test_data.copy()
        data['amount'] = '1000000000.00'
        result = self.validator.validate_input(data)
        self.assertFalse(result['valid'])
        self.assertIn("Amount exceeds maximum limit", result['errors'])

    def test_9_validate_amount_invalid_format(self):
        """Test validation with invalid amount format"""
        data = self.base_test_data.copy()
        data['amount'] = 'invalid'
        result = self.validator.validate_input(data)
        self.assertFalse(result['valid'])
        self.assertIn("Invalid amount format", result['errors'])

    def test_10_validate_date_future(self):
        """Test validation with future date"""
        data = self.base_test_data.copy()
        future_date = datetime.now() + timedelta(days=1)
        data['date'] = future_date.strftime('%Y-%m-%d')
        result = self.validator.validate_input(data)
        self.assertFalse(result['valid'])
        self.assertIn("Future date not allowed", result['errors'])

    def test_11_validate_date_old_payment(self):
        """Test validation with old payment date"""
        data = self.base_test_data.copy()
        old_date = datetime.now() - timedelta(days=32)  # Previous month
        data['date'] = old_date.strftime('%Y-%m-%d')
        result = self.validator.validate_input(data)
        self.assertTrue(result['valid'])
        self.assertIn("CNP verification required for old payment", result['warnings'])

    def test_12_validate_date_invalid_format(self):
        """Test validation with invalid date format"""
        data = self.base_test_data.copy()
        data['date'] = '2025/01/01'  # Wrong format
        result = self.validator.validate_input(data)
        self.assertFalse(result['valid'])
        self.assertIn("Invalid date format (YYYY-MM-DD)", result['errors'])

    def test_13_cross_reference_check_match(self):
        """Test cross-reference checking with matching record"""
        data = self.base_test_data.copy()
        data['amount'] = '15500.00'  # Above threshold
        
        # Create mock file handler
        class MockFileHandler:
            def read_file(self, file_type):
                return [{
                    'reference': 'TEST-2025-001',
                    'amount': '15600.00',  # Within 1% tolerance
                    'date': datetime.now().strftime('%Y-%m-%d')
                }]
        
        result = self.validator.cross_reference_check(data, MockFileHandler())
        self.assertTrue(len(result['matches']) > 0)

    def test_14_cross_reference_check_no_match(self):
        """Test cross-reference checking with no matching record"""
        data = self.base_test_data.copy()
        
        # Create mock file handler
        class MockFileHandler:
            def read_file(self, file_type):
                return [{
                    'reference': 'DIFFERENT-REF',
                    'amount': '10000.00',
                    'date': datetime.now().strftime('%Y-%m-%d')
                }]
        
        result = self.validator.cross_reference_check(data, MockFileHandler())
        self.assertEqual(len(result['matches']), 0)

    def test_15_cross_reference_check_threshold(self):
        """Test cross-reference checking with amount threshold"""
        data = self.base_test_data.copy()
        data['amount'] = '14999.99'  # Below threshold
        
        # Create mock file handler
        class MockFileHandler:
            def read_file(self, file_type):
                return [{
                    'reference': 'TEST-2025-001',
                    'amount': '15000.00',  # Different amount
                    'date': datetime.now().strftime('%Y-%m-%d')
                }]
        
        result = self.validator.cross_reference_check(data, MockFileHandler())
        self.assertEqual(len(result['matches']), 0)  # Should not match as amounts must be exact below threshold

if __name__ == '__main__':
    unittest.main()
