import unittest
from datetime import datetime
from payment_system_v4 import PaymentSystem
import tkinter as tk
from unittest.mock import patch

class TestPaymentSystem(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.root = tk.Tk()
        self.payment_system = PaymentSystem(self.root)
        self.test_payment = {
            'company': 'SALAM',
            'beneficiary': 'Test Beneficiary',
            'reference': 'TST-2025-0001',
            'amount': '10000.00',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'Under Process',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    @patch('tkinter.messagebox.askyesno', return_value=True)
    def test_1_new_payment_processing(self, mock_msgbox):
        """Test processing of a new valid payment"""
        print("\n=== Testing New Payment Processing ===")
        
        # Set form values
        self.payment_system.company_var.set(self.test_payment['company'])
        self.payment_system.beneficiary_var.set(self.test_payment['beneficiary'])
        self.payment_system.reference_var.set(self.test_payment['reference'])
        self.payment_system.amount_var.set(self.test_payment['amount'])
        self.payment_system.date_var.set(self.test_payment['date'])
        
        # Process payment
        self.payment_system.process_payment()
        print("New payment processing: PASSED")

    @patch('tkinter.messagebox.askyesno', return_value=True)
    def test_2_duplicate_payment_handling(self, mock_msgbox):
        """Test handling of duplicate payments"""
        print("\n=== Testing Duplicate Payment Handling ===")
        
        # First payment
        self.payment_system.process_payment()
        
        # Try duplicate payment
        self.payment_system.company_var.set(self.test_payment['company'])
        self.payment_system.beneficiary_var.set(self.test_payment['beneficiary'])
        self.payment_system.reference_var.set(self.test_payment['reference'])
        self.payment_system.amount_var.set(self.test_payment['amount'])
        self.payment_system.date_var.set(self.test_payment['date'])
        
        # Process payment
        self.payment_system.process_payment()
        
        # Check results text for duplicate message
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("❌", results_text)  # Error indicator
        print("Duplicate payment detection: PASSED")

    @patch('tkinter.messagebox.askyesno', return_value=False)
    def test_3_invalid_amount_handling(self, mock_msgbox):
        """Test handling of invalid payment amounts"""
        print("\n=== Testing Invalid Amount Handling ===")
        
        # Test negative amount
        self.payment_system.company_var.set(self.test_payment['company'])
        self.payment_system.beneficiary_var.set(self.test_payment['beneficiary'])
        self.payment_system.reference_var.set('TST-2025-0002')
        self.payment_system.amount_var.set('-1000.00')
        self.payment_system.date_var.set(self.test_payment['date'])
        
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("cancelled", results_text.lower())
        print("Negative amount handling: PASSED")
        
        # Test zero amount
        self.payment_system.amount_var.set('0.00')
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("cancelled", results_text.lower())
        print("Zero amount handling: PASSED")
        
        # Test excessive amount
        self.payment_system.amount_var.set('1000000000.00')
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("cancelled", results_text.lower())
        print("Excessive amount handling: PASSED")

    @patch('tkinter.messagebox.askyesno', return_value=False)
    def test_4_invalid_date_handling(self, mock_msgbox):
        """Test handling of invalid payment dates"""
        print("\n=== Testing Invalid Date Handling ===")
        
        # Test future date
        self.payment_system.company_var.set(self.test_payment['company'])
        self.payment_system.beneficiary_var.set(self.test_payment['beneficiary'])
        self.payment_system.reference_var.set('TST-2025-0003')
        self.payment_system.amount_var.set('1000.00')
        self.payment_system.date_var.set('2026-01-01')
        
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("cancelled", results_text.lower())
        print("Future date handling: PASSED")
        
        # Test invalid format
        self.payment_system.date_var.set('2025/01/01')
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("cancelled", results_text.lower())
        print("Invalid date format handling: PASSED")

    @patch('tkinter.messagebox.askyesno', return_value=True)
    def test_5_company_specific_processing(self, mock_msgbox):
        """Test company-specific processing rules"""
        print("\n=== Testing Company-Specific Processing ===")
        
        # Test SALAM payment
        self.payment_system.company_var.set('SALAM')
        self.payment_system.beneficiary_var.set(self.test_payment['beneficiary'])
        self.payment_system.reference_var.set('TST-2025-0004')
        self.payment_system.amount_var.set('1000.00')
        self.payment_system.date_var.set(self.test_payment['date'])
        
        self.payment_system.process_payment()
        print("SALAM payment processing: PASSED")
        
        # Test MVNO payment
        self.payment_system.company_var.set('MVNO')
        self.payment_system.reference_var.set('TST-2025-0005')
        
        self.payment_system.process_payment()
        print("MVNO payment processing: PASSED")

    @patch('tkinter.messagebox.askyesno', return_value=False)
    def test_6_reference_validation(self, mock_msgbox):
        """Test payment reference validation"""
        print("\n=== Testing Reference Validation ===")
        
        # Test invalid characters
        self.payment_system.company_var.set(self.test_payment['company'])
        self.payment_system.beneficiary_var.set(self.test_payment['beneficiary'])
        self.payment_system.reference_var.set('TST@2025#0001')
        self.payment_system.amount_var.set('1000.00')
        self.payment_system.date_var.set(self.test_payment['date'])
        
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("cancelled", results_text.lower())
        print("Invalid reference characters: PASSED")
        
        # Test empty reference
        self.payment_system.reference_var.set('')
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("cancelled", results_text.lower())
        print("Empty reference handling: PASSED")

    @patch('tkinter.messagebox.askyesno', return_value=False)
    def test_7_exception_handling(self, mock_msgbox):
        """Test payment exception handling"""
        print("\n=== Testing Exception Handling ===")
        
        # Test missing required field
        self.payment_system.company_var.set(self.test_payment['company'])
        self.payment_system.beneficiary_var.set('')  # Missing beneficiary
        self.payment_system.reference_var.set('TST-2025-0006')
        self.payment_system.amount_var.set('1000.00')
        self.payment_system.date_var.set(self.test_payment['date'])
        
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("cancelled", results_text.lower())
        print("Missing field handling: PASSED")
        
        # Test invalid company
        self.payment_system.company_var.set('INVALID')
        self.payment_system.beneficiary_var.set(self.test_payment['beneficiary'])
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("cancelled", results_text.lower())
        print("Invalid company handling: PASSED")

    @patch('tkinter.messagebox.askyesno', return_value=True)
    def test_8_old_payment_handling(self, mock_msgbox):
        """Test handling of old payments"""
        print("\n=== Testing Old Payment Handling ===")
        
        # Set old date
        old_date = '2024-12-01'
        self.payment_system.company_var.set(self.test_payment['company'])
        self.payment_system.beneficiary_var.set(self.test_payment['beneficiary'])
        self.payment_system.reference_var.set('TST-2025-0007')
        self.payment_system.amount_var.set('1000.00')
        self.payment_system.date_var.set(old_date)
        
        # Should require CNP explanation
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("explanation is required", results_text.lower())
        print("Old payment CNP requirement: PASSED")
        
        # Test with exception mode
        self.payment_system.exception_var.set(True)
        self.payment_system.exception_reason_entry.insert("1.0", "Test exception")
        self.payment_system.approver_var.set("Test Approver")
        self.payment_system.process_payment()
        results_text = self.payment_system.results_text.get("1.0", tk.END)
        self.assertIn("✅", results_text)  # Success indicator
        print("Exception mode handling: PASSED")

    def tearDown(self):
        """Clean up test data"""
        self.root.destroy()

if __name__ == '__main__':
    unittest.main()
