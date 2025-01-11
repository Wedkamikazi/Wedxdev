import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from datetime import datetime
from payment_system_v4 import PaymentSystem

class TestPaymentSystem(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        with patch('payment_system_v4.ValidationSystem'), \
             patch('payment_system_v4.FileOperations'), \
             patch('payment_system_v4.StatusTracker'), \
             patch('payment_system_v4.ExceptionHandler'), \
             patch('payment_system_v4.AuditTrail'):
            self.payment_system = PaymentSystem(self.root)
            
        # Create text widget for results
        self.payment_system.results_text = tk.Text(self.root)
        
    def tearDown(self):
        self.root.destroy()
        
    def test_setup_variables(self):
        """Test initialization of system variables"""
        self.assertIsInstance(self.payment_system.company_var, tk.StringVar)
        self.assertIsInstance(self.payment_system.beneficiary_var, tk.StringVar)
        self.assertIsInstance(self.payment_system.reference_var, tk.StringVar)
        self.assertIsInstance(self.payment_system.amount_var, tk.StringVar)
        self.assertIsInstance(self.payment_system.date_var, tk.StringVar)
        
        # Check default date
        current_date = datetime.now().strftime('%Y-%m-%d')
        self.assertEqual(self.payment_system.date_var.get(), current_date)
        
    def test_clear_form(self):
        """Test form clearing functionality"""
        # Set test values
        self.payment_system.company_var.set('SALAM')
        self.payment_system.beneficiary_var.set('Test Beneficiary')
        self.payment_system.reference_var.set('TEST-REF-001')
        self.payment_system.amount_var.set('1000.00')
        
        # Clear form
        self.payment_system.clear_form()
        
        # Verify all fields are cleared except date
        self.assertEqual(self.payment_system.company_var.get(), '')
        self.assertEqual(self.payment_system.beneficiary_var.get(), '')
        self.assertEqual(self.payment_system.reference_var.get(), '')
        self.assertEqual(self.payment_system.amount_var.get(), '')
        
    def test_validate_payment(self):
        """Test payment validation"""
        # Setup test data
        test_data = {
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary',
            'reference': 'TEST-REF-001',
            'amount': '1000.00',
            'date': '2025-01-12',
            'status': 'Under Process',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Set form values
        self.payment_system.company_var.set(test_data['company'])
        self.payment_system.beneficiary_var.set(test_data['beneficiary'])
        self.payment_system.reference_var.set(test_data['reference'])
        self.payment_system.amount_var.set(test_data['amount'])
        self.payment_system.date_var.set(test_data['date'])
        
        # Mock validator
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        self.payment_system.validator.validate_input = MagicMock(return_value=validation_result)
        
        # Add display_validation_results method
        self.payment_system.display_validation_results = MagicMock()
        
        # Test validation
        result = self.payment_system.validate_payment()
        
        # Verify validator was called with correct data
        self.payment_system.validator.validate_input.assert_called_once_with(test_data)
        self.payment_system.display_validation_results.assert_called_once_with(validation_result)
        self.assertTrue(result)
        
    def test_process_payment(self):
        """Test payment processing"""
        # Setup test data
        test_data = {
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary',
            'reference': 'TEST-REF-001',
            'amount': '1000.00',
            'date': '2025-01-12',
            'status': 'Under Process',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Set form values
        self.payment_system.company_var.set(test_data['company'])
        self.payment_system.beneficiary_var.set(test_data['beneficiary'])
        self.payment_system.reference_var.set(test_data['reference'])
        self.payment_system.amount_var.set(test_data['amount'])
        self.payment_system.date_var.set(test_data['date'])
        
        # Mock components
        self.payment_system.validator.validate_input = MagicMock(return_value={
            'valid': True,
            'errors': [],
            'warnings': []
        })
        self.payment_system.file_ops.verify_payment = MagicMock(return_value={
            'matches': False,
            'details': [],
            'files': ['BS-Salam', 'CNP-Salam', 'Treasury']
        })
        
        # Add required methods
        self.payment_system.display_validation_results = MagicMock()
        self.payment_system.display_verification_results = MagicMock()
        self.payment_system.save_payment = MagicMock()
        self.payment_system.show_success_message = MagicMock()
        
        # Test processing
        with patch('tkinter.messagebox.askyesno', return_value=True):
            self.payment_system.process_payment()
        
        # Verify operations
        self.payment_system.validator.validate_input.assert_called_once_with(test_data)
        self.payment_system.file_ops.verify_payment.assert_called_once_with(test_data)
        self.payment_system.save_payment.assert_called_once_with(test_data)
        
    def test_get_payment_data(self):
        """Test payment data retrieval"""
        # Setup test data
        test_data = {
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary',
            'reference': 'TEST-REF-001',
            'amount': '1000.00',
            'date': '2025-01-12'
        }
        
        # Set form values
        self.payment_system.company_var.set(test_data['company'])
        self.payment_system.beneficiary_var.set(test_data['beneficiary'])
        self.payment_system.reference_var.set(test_data['reference'])
        self.payment_system.amount_var.set(test_data['amount'])
        self.payment_system.date_var.set(test_data['date'])
        
        # Get payment data
        payment_data = self.payment_system.get_payment_data()
        
        # Verify core data
        self.assertEqual(payment_data['company'], test_data['company'])
        self.assertEqual(payment_data['beneficiary'], test_data['beneficiary'])
        self.assertEqual(payment_data['reference'], test_data['reference'])
        self.assertEqual(payment_data['amount'], test_data['amount'])
        self.assertEqual(payment_data['date'], test_data['date'])
        
        # Verify additional fields
        self.assertEqual(payment_data['status'], 'Under Process')
        self.assertIsNotNone(payment_data['timestamp'])
        
    def test_check_status(self):
        """Test payment status checking"""
        # Setup test data
        reference = 'TEST-REF-001'
        self.payment_system.reference_var.set(reference)
        
        # Mock components
        status_data = {'status': 'Completed', 'timestamp': '2025-01-11 13:00:00'}
        self.payment_system.status_tracker.update_status = MagicMock(return_value=status_data)
        self.payment_system.exception_handler.get_open_exceptions = MagicMock(return_value=[])
        
        # Add display method
        self.payment_system.display_status_results = MagicMock()
        
        # Test status check
        with patch.object(self.payment_system, 'show_in_results'), \
             patch.object(self.payment_system, 'log_audit'):
            self.payment_system.check_status()
            
            # Verify operations
            self.payment_system.status_tracker.update_status.assert_called_once_with(reference)
            self.payment_system.exception_handler.get_open_exceptions.assert_called_once_with(reference)
            self.payment_system.display_status_results.assert_called_once_with(status_data, [])

    def test_display_validation_results(self):
        """Test displaying validation results"""
        # Setup test data
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': ['Warning: Large payment amount']
        }
        
        # Test display
        with patch.object(self.payment_system, 'show_in_results') as mock_show:
            self.payment_system.display_validation_results(validation_result)
            mock_show.assert_called_once()
            
            # Verify the call contains validation info
            call_args = mock_show.call_args[0][0]
            self.assertIn('=== Validation Results ===', call_args)
            self.assertIn('Status: Valid', call_args)
            self.assertIn('Warning: Large payment amount', call_args)

    def test_display_verification_results(self):
        """Test displaying verification results"""
        # Setup test data
        verification_result = {
            'matches': False,
            'details': [],
            'files': ['BS-Salam', 'CNP-Salam', 'Treasury']
        }
        
        # Test display
        with patch.object(self.payment_system, 'show_in_results') as mock_show:
            self.payment_system.display_verification_results(verification_result)
            mock_show.assert_called_once()
            
            # Verify the call contains verification info
            call_args = mock_show.call_args[0][0]
            self.assertIn('=== Verification Results ===', call_args)
            self.assertIn('Status: No matches found', call_args)
            for file in verification_result['files']:
                self.assertIn(file, call_args)

    def test_display_status_results(self):
        """Test displaying status results"""
        # Setup test data
        status_data = {
            'status': 'Completed',
            'timestamp': '2025-01-11 13:00:00',
            'details': 'Payment processed successfully'
        }
        exceptions = [{
            'type': 'Processing_Warning',
            'description': 'Delayed processing',
            'timestamp': '2025-01-11 12:55:00'
        }]
        
        # Test display
        with patch.object(self.payment_system, 'show_in_results') as mock_show:
            self.payment_system.display_status_results(status_data, exceptions)
            mock_show.assert_called_once()
            
            # Verify the call contains status info
            call_args = mock_show.call_args[0][0]
            self.assertIn('=== Payment Status ===', call_args)
            self.assertIn('Status: Completed', call_args)
            self.assertIn('2025-01-11 13:00:00', call_args)
            self.assertIn('Processing_Warning', call_args)
            self.assertIn('Delayed processing', call_args)

    def test_show_success_message(self):
        """Test success message display"""
        with patch('tkinter.messagebox.showinfo') as mock_showinfo:
            self.payment_system.show_success_message()
            mock_showinfo.assert_called_once_with(
                "Success",
                "Payment processed successfully!"
            )

    def test_save_payment(self):
        """Test payment saving functionality"""
        # Setup test data
        payment_data = {
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary',
            'reference': 'TEST-REF-001',
            'amount': '1000.00',
            'date': '2025-01-12',
            'status': 'Under Process',
            'timestamp': '2025-01-11 13:08:08'
        }
        
        # Mock file operations
        self.payment_system.file_ops.save_payment = MagicMock()
        
        # Test saving
        with patch.object(self.payment_system, 'log_audit'):
            self.payment_system.save_payment(payment_data)
            
            # Verify save was called
            self.payment_system.file_ops.save_payment.assert_called_once_with(payment_data)

    def test_extreme_input_validation(self):
        """Test validation with extreme edge cases"""
        test_cases = [
            {
                'company': 'SALAM' * 100,  # Very long company name
                'beneficiary': '🌟星星' * 50,  # Unicode characters repeated
                'reference': 'REF-\u200B\u200B-001',  # Zero-width spaces
                'amount': '999999999999.99',  # Maximum possible amount
                'date': '2025-01-11',
                'status': 'Under Process',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'company': '',  # Empty company
                'beneficiary': ' ',  # Just whitespace
                'reference': '0' * 255,  # Maximum length reference
                'amount': '0.01',  # Minimum amount
                'date': '2025-01-11',
                'status': 'Under Process',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'company': 'MVNO',
                'beneficiary': 'Test; DROP TABLE payments;--',  # SQL Injection attempt
                'reference': '<script>alert("XSS")</script>',  # XSS attempt
                'amount': '-1000.00',  # Negative amount
                'date': '2025-13-32',  # Invalid date
                'status': 'Under Process',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]

        for test_data in test_cases:
            # Set form values
            self.payment_system.company_var.set(test_data['company'])
            self.payment_system.beneficiary_var.set(test_data['beneficiary'])
            self.payment_system.reference_var.set(test_data['reference'])
            self.payment_system.amount_var.set(test_data['amount'])
            self.payment_system.date_var.set(test_data['date'])

            # Mock validator with appropriate response
            validation_result = {
                'valid': False,
                'errors': ['Invalid input detected'],
                'warnings': ['Extreme values detected']
            }
            self.payment_system.validator.validate_input = MagicMock(return_value=validation_result)
            self.payment_system.display_validation_results = MagicMock()

            # Get expected data
            expected_data = {
                'company': test_data['company'],
                'beneficiary': test_data['beneficiary'],
                'reference': test_data['reference'],
                'amount': test_data['amount'],
                'date': test_data['date'],
                'status': 'Under Process',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Test validation
            with patch.object(self.payment_system, 'get_payment_data', return_value=expected_data):
                result = self.payment_system.validate_payment()
                self.assertFalse(result)
                self.payment_system.validator.validate_input.assert_called_with(expected_data)

    def test_concurrent_operations(self):
        """Test handling of concurrent operations"""
        # Setup test data for concurrent operations
        test_data = {
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary',
            'reference': 'TEST-REF-001',
            'amount': '1000.00',
            'date': '2025-01-11',
            'status': 'Under Process',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Set form values
        self.payment_system.company_var.set(test_data['company'])
        self.payment_system.beneficiary_var.set(test_data['beneficiary'])
        self.payment_system.reference_var.set(test_data['reference'])
        self.payment_system.amount_var.set(test_data['amount'])
        self.payment_system.date_var.set(test_data['date'])

        # Mock components
        self.payment_system.validator.validate_input = MagicMock(return_value={
            'valid': True,
            'errors': [],
            'warnings': []
        })
        self.payment_system.file_ops.verify_payment = MagicMock(side_effect=[
            {'matches': False, 'details': [], 'files': ['BS-Salam']},  # First check
            {'matches': True, 'details': ['Payment already exists'], 'files': ['BS-Salam']}  # Second check (concurrent)
        ])
        
        # Mock additional methods
        self.payment_system.display_validation_results = MagicMock()
        self.payment_system.display_verification_results = MagicMock()
        self.payment_system.save_payment = MagicMock()
        self.payment_system.show_success_message = MagicMock()

        # Test concurrent save attempts
        with patch.object(self.payment_system, 'log_audit'), \
             patch.object(self.payment_system, 'handle_exception'), \
             patch.object(self.payment_system, 'show_in_results'), \
             patch.object(self.payment_system, 'get_payment_data', return_value=test_data), \
             patch('tkinter.messagebox.askyesno', return_value=True):
            
            # First attempt
            self.payment_system.process_payment()
            self.payment_system.file_ops.verify_payment.assert_called_with(test_data)
            self.payment_system.handle_exception.assert_not_called()

            # Second attempt (should detect concurrent modification)
            self.payment_system.process_payment()
            self.payment_system.handle_exception.assert_called()

    def test_system_resilience(self):
        """Test system resilience against various failure scenarios"""
        # Test file system errors
        payment_data = {
            'reference': 'TEST-REF-001',
            'company': 'SALAM',
            'amount': '1000.00',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.payment_system.file_ops.save_payment = MagicMock(side_effect=IOError("File system error"))
        self.payment_system.handle_exception = MagicMock()  # Reset mock
        
        with patch.object(self.payment_system, 'log_audit'):
            try:
                self.payment_system.save_payment(payment_data)
            except IOError:
                pass
            
            self.payment_system.handle_exception.assert_called_once()

        # Test network timeouts
        self.payment_system.reference_var.set('TEST-REF-001')  # Set reference for status check
        self.payment_system.status_tracker.update_status = MagicMock(side_effect=TimeoutError("Network timeout"))
        self.payment_system.handle_exception = MagicMock()  # Reset mock
        
        with patch.object(self.payment_system, 'log_audit'), \
             patch.object(self.payment_system, 'show_in_results'):
            
            self.payment_system.check_status()
            self.payment_system.handle_exception.assert_called_once()

    def test_unicode_handling(self):
        """Test handling of various Unicode characters and encodings"""
        test_cases = [
            {
                'beneficiary': '测试收款人',  # Chinese characters
                'reference': 'REF-测试-001'
            },
            {
                'beneficiary': 'مستفيد الاختبار',  # Arabic characters
                'reference': 'REF-اختبار-001'
            },
            {
                'beneficiary': 'Тестовый получатель',  # Cyrillic characters
                'reference': 'REF-тест-001'
            },
            {
                'beneficiary': '🏦🏧💰',  # Emojis
                'reference': 'REF-💸-001'
            }
        ]

        for test_case in test_cases:
            # Test display in results
            with patch.object(self.payment_system, 'show_in_results') as mock_show:
                self.payment_system.display_validation_results({
                    'valid': True,
                    'errors': [],
                    'warnings': [f'Unicode test: {test_case["beneficiary"]}']
                })
                mock_show.assert_called_once()

            # Test file operations
            self.payment_system.file_ops.save_payment = MagicMock()
            payment_data = {
                'company': 'SALAM',
                'beneficiary': test_case['beneficiary'],
                'reference': test_case['reference'],
                'amount': '1000.00',
                'date': '2025-01-11',
                'status': 'Under Process',
                'timestamp': '2025-01-11 13:10:41'
            }
            
            with patch.object(self.payment_system, 'log_audit'):
                self.payment_system.save_payment(payment_data)
                self.payment_system.file_ops.save_payment.assert_called_with(payment_data)

    def test_memory_management(self):
        """Test handling of large data sets and memory management"""
        # Generate large dataset
        large_results = {
            'valid': True,
            'errors': [],
            'warnings': [f'Warning {i}' for i in range(1000)]  # Large number of warnings
        }
        
        # Test memory efficient display
        with patch.object(self.payment_system, 'show_in_results') as mock_show:
            self.payment_system.display_validation_results(large_results)
            mock_show.assert_called_once()
            
            # Verify output is chunked
            call_args = mock_show.call_args[0][0]
            self.assertLess(len(call_args.split('\n')), 1100)  # Ensure reasonable output size

    def test_extreme_stress(self):
        """Test system under extreme stress conditions"""
        # Generate large batch of test payments
        stress_payments = []
        unicode_chars = '🌟星💰₿€¥£₹元円₽₪₱฿₭₫₴₮'
        special_chars = '\u200B\u200C\u200D\uFEFF\u200E\u200F'
        
        for i in range(1000):  # Test with 1000 concurrent payments
            payment = {
                'company': f"{'SALAM' if i % 2 == 0 else 'MVNO'}{special_chars * (i % 5)}",
                'beneficiary': f"Test{unicode_chars * (i % 10)}_{i}",
                'reference': f"REF-{special_chars}-{str(i).zfill(10)}",
                'amount': f"{(i + 0.01):.2f}",
                'date': '2025-01-11',
                'status': 'Under Process',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            stress_payments.append(payment)

        # Mock components for stress test
        self.payment_system.validator.validate_input = MagicMock(return_value={
            'valid': True, 'errors': [], 'warnings': []
        })
        self.payment_system.file_ops.verify_payment = MagicMock(return_value={
            'matches': False, 'details': [], 'files': ['BS-Salam']
        })
        self.payment_system.file_ops.save_payment = MagicMock()
        self.payment_system.display_validation_results = MagicMock()
        self.payment_system.display_verification_results = MagicMock()
        self.payment_system.show_success_message = MagicMock()

        # Process batch of payments
        with patch.object(self.payment_system, 'log_audit'), \
             patch.object(self.payment_system, 'show_in_results'), \
             patch('tkinter.messagebox.askyesno', return_value=True):
            
            for payment in stress_payments:
                # Set form values
                self.payment_system.company_var.set(payment['company'])
                self.payment_system.beneficiary_var.set(payment['beneficiary'])
                self.payment_system.reference_var.set(payment['reference'])
                self.payment_system.amount_var.set(payment['amount'])
                self.payment_system.date_var.set(payment['date'])
                
                with patch.object(self.payment_system, 'get_payment_data', return_value=payment):
                    self.payment_system.process_payment()

            # Verify system handled the stress
            self.assertEqual(self.payment_system.validator.validate_input.call_count, 1000)
            self.assertEqual(self.payment_system.file_ops.verify_payment.call_count, 1000)
            self.assertEqual(self.payment_system.file_ops.save_payment.call_count, 1000)

    def test_malicious_input(self):
        """Test system resilience against malicious inputs"""
        malicious_inputs = [
            # SQL Injection attempts
            "'; DROP TABLE payments; --",
            "' UNION SELECT * FROM users; --",
            "' OR '1'='1",
            # XSS attempts
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src='x' onerror='alert(1)'>",
            # Command injection attempts
            "$(rm -rf /)",
            "`rm -rf /`",
            "& del /f /s /q *",
            # Buffer overflow attempts
            "A" * 10000,
            "%" * 10000,
            "\x00" * 10000,
            # Unicode exploits
            "نظام_الدفع" * 100,
            "システム" * 100,
            "🏦" * 1000,
            # Path traversal attempts
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config",
            "file:///etc/passwd",
            # Special characters
            "\x00\x01\x02\x03\x04\x05",
            "\u0000\u0001\u0002\u0003",
            "\r\n\t\b\f\v" * 100
        ]

        for malicious_input in malicious_inputs:
            test_data = {
                'company': malicious_input,
                'beneficiary': malicious_input,
                'reference': malicious_input[:50],  # Truncate for reference
                'amount': '1000.00',
                'date': '2025-01-11',
                'status': 'Under Process',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Set form values
            self.payment_system.company_var.set(test_data['company'])
            self.payment_system.beneficiary_var.set(test_data['beneficiary'])
            self.payment_system.reference_var.set(test_data['reference'])
            self.payment_system.amount_var.set(test_data['amount'])
            self.payment_system.date_var.set(test_data['date'])

            # Mock validation to simulate security checks
            self.payment_system.validator.validate_input = MagicMock(return_value={
                'valid': False,
                'errors': ['Security violation detected'],
                'warnings': ['Potentially malicious input detected']
            })
            self.payment_system.display_validation_results = MagicMock()

            # Test processing
            with patch.object(self.payment_system, 'get_payment_data', return_value=test_data), \
                 patch.object(self.payment_system, 'log_audit'), \
                 patch.object(self.payment_system, 'handle_exception'):
                
                result = self.payment_system.validate_payment()
                self.assertFalse(result)
                self.payment_system.validator.validate_input.assert_called_with(test_data)

    def test_race_conditions(self):
        """Test handling of potential race conditions"""
        test_data = {
            'company': 'SALAM',
            'beneficiary': 'Race Test',
            'reference': 'RACE-001',
            'amount': '1000.00',
            'date': '2025-01-11',
            'status': 'Under Process',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Simulate race conditions in file operations
        race_responses = [
            {'matches': False, 'details': [], 'files': ['BS-Salam']},
            {'matches': True, 'details': ['Concurrent modification detected'], 'files': ['BS-Salam']},
            IOError("File locked by another process"),
            TimeoutError("Operation timed out"),
            PermissionError("Access denied"),
        ]

        self.payment_system.file_ops.verify_payment = MagicMock(side_effect=race_responses)
        self.payment_system.validator.validate_input = MagicMock(return_value={
            'valid': True, 'errors': [], 'warnings': []
        })
        
        # Set up form
        self.payment_system.company_var.set(test_data['company'])
        self.payment_system.beneficiary_var.set(test_data['beneficiary'])
        self.payment_system.reference_var.set(test_data['reference'])
        self.payment_system.amount_var.set(test_data['amount'])
        self.payment_system.date_var.set(test_data['date'])

        # Test rapid-fire processing attempts
        with patch.object(self.payment_system, 'log_audit'), \
             patch.object(self.payment_system, 'handle_exception'), \
             patch.object(self.payment_system, 'show_in_results'), \
             patch.object(self.payment_system, 'get_payment_data', return_value=test_data), \
             patch('tkinter.messagebox.askyesno', return_value=True):
            
            for _ in range(5):  # Test all race conditions
                try:
                    self.payment_system.process_payment()
                except (IOError, TimeoutError, PermissionError):
                    pass  # Expected exceptions
                
            # Verify all race conditions were handled
            self.payment_system.handle_exception.assert_called()
            self.assertEqual(self.payment_system.file_ops.verify_payment.call_count, 5)

    def test_memory_limits(self):
        """Test system behavior under memory pressure"""
        # Generate massive result sets
        huge_results = {
            'valid': True,
            'errors': ['Error ' + ('X' * 1000) for _ in range(100)],
            'warnings': ['Warning ' + ('Y' * 1000) for _ in range(100)],
            'details': ['Detail ' + ('Z' * 1000) for _ in range(100)]
        }

        # Test display methods under memory pressure
        with patch.object(self.payment_system, 'show_in_results') as mock_show:
            self.payment_system.display_validation_results(huge_results)
            mock_show.assert_called_once()
            
            # Verify output is reasonably sized
            call_args = mock_show.call_args[0][0]
            self.assertLess(len(call_args), 100000)  # Ensure output is capped

        # Test status display with large exception list
        status_data = {
            'status': 'Processing',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'details': 'X' * 10000
        }
        exceptions = [
            {
                'type': f'Error_{i}',
                'description': 'X' * 1000,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            for i in range(100)
        ]

        with patch.object(self.payment_system, 'show_in_results') as mock_show:
            self.payment_system.display_status_results(status_data, exceptions)
            mock_show.assert_called_once()
            
            # Verify output is truncated appropriately
            call_args = mock_show.call_args[0][0]
            self.assertLess(len(call_args), 100000)

    def test_payment_confirmation(self):
        """Test payment confirmation dialog"""
        test_data = {
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary',
            'reference': 'TEST-REF-001',
            'amount': '1000.00',
            'date': '2025-01-11',
            'status': 'Under Process',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Test when user confirms
        with patch('tkinter.messagebox.askyesno', return_value=True) as mock_dialog:
            result = self.payment_system.confirm_payment(test_data)
            self.assertTrue(result)
            mock_dialog.assert_called_once()
            
        # Test when user cancels
        with patch('tkinter.messagebox.askyesno', return_value=False) as mock_dialog:
            result = self.payment_system.confirm_payment(test_data)
            self.assertFalse(result)
            mock_dialog.assert_called_once()
            
        # Test full payment process with confirmation
        self.payment_system.validator.validate_input = MagicMock(return_value={
            'valid': True,
            'errors': [],
            'warnings': []
        })
        self.payment_system.file_ops.verify_payment = MagicMock(return_value={
            'matches': False,
            'details': [],
            'files': ['BS-Salam']
        })
        self.payment_system.file_ops.save_payment = MagicMock()
        
        # Set form values
        self.payment_system.company_var.set(test_data['company'])
        self.payment_system.beneficiary_var.set(test_data['beneficiary'])
        self.payment_system.reference_var.set(test_data['reference'])
        self.payment_system.amount_var.set(test_data['amount'])
        self.payment_system.date_var.set(test_data['date'])
        
        # Test when user cancels - payment should not be saved
        with patch('tkinter.messagebox.askyesno', return_value=False), \
             patch.object(self.payment_system, 'log_audit'), \
             patch.object(self.payment_system, 'show_success_message'):
            
            self.payment_system.process_payment()
            self.payment_system.file_ops.save_payment.assert_not_called()
            
        # Test when user confirms - payment should be saved
        with patch('tkinter.messagebox.askyesno', return_value=True), \
             patch.object(self.payment_system, 'log_audit'), \
             patch.object(self.payment_system, 'show_success_message'):
            
            self.payment_system.process_payment()
            self.payment_system.file_ops.save_payment.assert_called_once()

if __name__ == '__main__':
    unittest.main()
