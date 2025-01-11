import tkinter as tk
from payment_system_v4 import PaymentSystem
import os

def test_verification():
    root = tk.Tk()
    payment_system = PaymentSystem(root)
    
    def setup_test_data():
        print("\nSetting up test data...")
        # Ensure data directory exists
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bank_statements/SALAM')
        os.makedirs(data_dir, exist_ok=True)
        
        # Create test bank statement with a known reference
        bs_file = os.path.join(data_dir, 'BS_SALAM_CURRENT.csv')
        print(f"Creating test file at: {bs_file}")
        # Always create the file with test data
        with open(bs_file, 'w', newline='') as f:
            f.write('reference,amount,date,status,timestamp\n')
            f.write('REF-001,1000.00,2025-01-11,Completed,2025-01-11 13:27:00\n')
        print("Test data setup complete.")
    
    def test_new_reference():
        print("\nTest 1: New Reference (Should Not Find Match)")
        print("=========================================")
        payment_system.company_var.set('SALAM')
        payment_system.beneficiary_var.set('Test Beneficiary')
        payment_system.reference_var.set('NEW-REF-999')  # New reference
        payment_system.amount_var.set('1000.00')
        
        # Get payment data and verify
        payment_data = payment_system.get_payment_data()
        verification_result = payment_system.file_ops.verify_payment(payment_data)
        print(f"Found matches: {verification_result['matches']}")
        print(f"Details: {verification_result['details']}")
        print(f"Files checked: {verification_result['files']}")
    
    def test_existing_reference():
        print("\nTest 2: Existing Reference (Should Find Match)")
        print("=========================================")
        payment_system.company_var.set('SALAM')
        payment_system.beneficiary_var.set('Test Beneficiary')
        payment_system.reference_var.set('REF-001')  # Existing reference
        payment_system.amount_var.set('1000.00')
        
        # Get payment data and verify
        payment_data = payment_system.get_payment_data()
        verification_result = payment_system.file_ops.verify_payment(payment_data)
        print(f"Found matches: {verification_result['matches']}")
        print(f"Details: {verification_result['details']}")
        print(f"Files checked: {verification_result['files']}")
    
    # Setup test data first
    setup_test_data()
    
    # Run tests after a short delay
    root.after(500, test_new_reference)
    root.after(1000, test_existing_reference)
    root.after(1500, root.destroy)  # Close after tests
    
    root.mainloop()

if __name__ == '__main__':
    test_verification()
