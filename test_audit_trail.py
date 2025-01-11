import unittest
import os
import csv
from datetime import datetime
from audit_trail import AuditTrail

class TestAuditTrail(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.audit_trail = AuditTrail()
        self.test_reference = "TEST-2025-0001"
        
        # Ensure audit log is empty at start
        if os.path.exists(self.audit_trail.audit_file):
            with open(self.audit_trail.audit_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'action', 'reference', 'details', 'user', 'status'])

    def test_1_log_system_start(self):
        """Test logging system startup"""
        self.audit_trail.log_action({
            'action': 'System_Start',
            'details': 'System initialized',
            'status': 'Active'
        })
        
        with open(self.audit_trail.audit_file, 'r', encoding='utf-8') as f:
            logs = list(csv.DictReader(f))
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['action'], 'System_Start')
            self.assertEqual(logs[0]['status'], 'Active')

    def test_2_log_payment_processing(self):
        """Test logging payment processing"""
        self.audit_trail.log_action({
            'action': 'Payment_Processing',
            'reference': self.test_reference,
            'details': 'Payment processed successfully',
            'status': 'Completed'
        })
        
        with open(self.audit_trail.audit_file, 'r', encoding='utf-8') as f:
            logs = list(csv.DictReader(f))
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['action'], 'Payment_Processing')
            self.assertEqual(logs[0]['reference'], self.test_reference)

    def test_3_log_validation_failure(self):
        """Test logging validation failures"""
        self.audit_trail.log_action({
            'action': 'Validation_Failed',
            'reference': self.test_reference,
            'details': 'Invalid amount format',
            'status': 'Failed'
        })
        
        with open(self.audit_trail.audit_file, 'r', encoding='utf-8') as f:
            logs = list(csv.DictReader(f))
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['action'], 'Validation_Failed')
            self.assertEqual(logs[0]['status'], 'Failed')

    def test_4_log_exception_handling(self):
        """Test logging exception handling"""
        self.audit_trail.log_action({
            'action': 'Exception_Handled',
            'reference': self.test_reference,
            'details': 'Old payment processed with approval',
            'status': 'Resolved'
        })
        
        with open(self.audit_trail.audit_file, 'r', encoding='utf-8') as f:
            logs = list(csv.DictReader(f))
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['action'], 'Exception_Handled')
            self.assertEqual(logs[0]['status'], 'Resolved')

    def test_5_log_file_operations(self):
        """Test logging file operations"""
        self.audit_trail.log_action({
            'action': 'File_Operation',
            'reference': self.test_reference,
            'details': 'Payment saved to treasury',
            'status': 'Success'
        })
        
        with open(self.audit_trail.audit_file, 'r', encoding='utf-8') as f:
            logs = list(csv.DictReader(f))
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['action'], 'File_Operation')
            self.assertEqual(logs[0]['status'], 'Success')

    def test_6_log_multiple_events(self):
        """Test logging multiple events in sequence"""
        events = [
            {
                'action': 'System_Start',
                'details': 'System initialized',
                'status': 'Active'
            },
            {
                'action': 'Payment_Processing',
                'reference': self.test_reference,
                'details': 'Payment validated',
                'status': 'In_Progress'
            },
            {
                'action': 'File_Operation',
                'reference': self.test_reference,
                'details': 'Payment saved',
                'status': 'Success'
            },
            {
                'action': 'Payment_Processing',
                'reference': self.test_reference,
                'details': 'Payment completed',
                'status': 'Completed'
            }
        ]
        
        for event in events:
            self.audit_trail.log_action(event)
        
        with open(self.audit_trail.audit_file, 'r', encoding='utf-8') as f:
            logs = list(csv.DictReader(f))
            self.assertEqual(len(logs), 4)
            self.assertEqual(logs[0]['action'], 'System_Start')
            self.assertEqual(logs[-1]['status'], 'Completed')

    def test_7_log_special_characters(self):
        """Test logging with special characters"""
        special_details = "Test@#$%^&*()_+ details"
        self.audit_trail.log_action({
            'action': 'Special_Test',
            'reference': self.test_reference,
            'details': special_details,
            'status': 'Completed'
        })
        
        with open(self.audit_trail.audit_file, 'r', encoding='utf-8') as f:
            logs = list(csv.DictReader(f))
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['details'], special_details)

    def test_8_log_unicode_characters(self):
        """Test logging with unicode characters"""
        unicode_details = "测试支付处理"
        self.audit_trail.log_action({
            'action': 'Unicode_Test',
            'reference': self.test_reference,
            'details': unicode_details,
            'status': 'Completed'
        })
        
        with open(self.audit_trail.audit_file, 'r', encoding='utf-8') as f:
            logs = list(csv.DictReader(f))
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]['details'], unicode_details)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.audit_trail.audit_file):
            with open(self.audit_trail.audit_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'action', 'reference', 'details', 'user', 'status'])

if __name__ == '__main__':
    unittest.main()
