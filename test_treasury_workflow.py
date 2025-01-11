import tkinter as tk
from payment_system_v4 import PaymentSystem
import os
from datetime import datetime

def test_treasury_workflow():
    root = tk.Tk()
    payment_system = PaymentSystem(root)
    
    def setup_test_environment():
        print("\nSetting up test environment...")
        # Ensure directories exist
        base_dir = os.path.dirname(os.path.abspath(__file__))
        directories = ['data/treasury', 'data/bank_statements/SALAM']
        for directory in directories:
            os.makedirs(os.path.join(base_dir, directory), exist_ok=True)
        
        # Create test bank statement (simulating existing paid payment)
        bs_file = os.path.join(base_dir, 'data/bank_statements/SALAM/BS_SALAM_CURRENT.csv')
        with open(bs_file, 'w', newline='') as f:
            f.write('reference,amount,date,status,timestamp\n')
            f.write('PAID-001,500.00,2025-01-11,Completed,2025-01-11 13:27:00\n')
        print("Test environment setup complete.")
    
    def test_new_payment():
        print("\nTest 1: New Payment to Treasury")
        print("==============================")
        # Set values for new payment
        payment_system.company_var.set('SALAM')
        payment_system.beneficiary_var.set('Test Beneficiary')
        payment_system.reference_var.set('NEW-REF-003')
        payment_system.amount_var.set('1500.00')
        payment_system.date_var.set('2025-01-11')
        
        # Process payment
        payment_system.process_payment()
        print("New payment test complete - check Treasury file")
    
    def verify_treasury_file():
        print("\nVerifying Treasury File:")
        treasury_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   'data/treasury/TREASURY_CURRENT.csv')
        if os.path.exists(treasury_file):
            with open(treasury_file, 'r') as f:
                print(f.read())
        else:
            print("Treasury file not found!")
    
    # Setup and run tests with delays
    root.after(500, setup_test_environment)
    root.after(1000, test_new_payment)
    root.after(3000, verify_treasury_file)
    root.after(3500, root.destroy)
    
    root.mainloop()

if __name__ == '__main__':
    test_treasury_workflow()
