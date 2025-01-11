import tkinter as tk
from payment_system_v4 import PaymentSystem
import os
from datetime import datetime

def test_payment_process():
    root = tk.Tk()
    payment_system = PaymentSystem(root)
    
    def setup_test_environment():
        print("\nSetting up test environment...")
        # Create test directories
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bank_statements/SALAM')
        os.makedirs(data_dir, exist_ok=True)
        
        # Create test bank statement
        bs_file = os.path.join(data_dir, 'BS_SALAM_CURRENT.csv')
        with open(bs_file, 'w', newline='') as f:
            f.write('reference,amount,date,status,timestamp\n')
            f.write('REF-001,1000.00,2025-01-11,Completed,2025-01-11 13:27:00\n')
        print("Test environment setup complete.")
    
    def test_duplicate_payment():
        print("\nTest 1: Duplicate Payment")
        print("========================")
        # Set values for existing payment
        payment_system.company_var.set('SALAM')
        payment_system.beneficiary_var.set('Test Beneficiary')
        payment_system.reference_var.set('REF-001')  # Existing reference
        payment_system.amount_var.set('1000.00')
        payment_system.date_var.set('2025-01-11')
        
        # Process payment
        payment_system.process_payment()
        print("Duplicate payment test complete - check results panel")
    
    def test_new_payment():
        print("\nTest 2: New Payment")
        print("==================")
        # Set values for new payment
        payment_system.company_var.set('SALAM')
        payment_system.beneficiary_var.set('New Beneficiary')
        payment_system.reference_var.set('NEW-REF-002')  # New reference
        payment_system.amount_var.set('2000.00')
        payment_system.date_var.set('2025-01-11')
        
        # Process payment
        payment_system.process_payment()
        print("New payment test complete - check results panel and confirmation dialog")
    
    # Setup and run tests with delays
    root.after(500, setup_test_environment)
    root.after(1000, test_duplicate_payment)
    root.after(3000, test_new_payment)  # Longer delay to see results of first test
    
    root.mainloop()

if __name__ == '__main__':
    test_payment_process()
