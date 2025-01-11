import tkinter as tk
from payment_system_v4 import PaymentSystem

def test_validation():
    root = tk.Tk()
    payment_system = PaymentSystem(root)
    
    def test_empty_fields():
        print("\nTest 1: Empty Fields Validation")
        print("==============================")
        # Clear all fields
        payment_system.clear_form()
        # Try to validate
        result = payment_system.validate_payment()
        print(f"Validation result (should be False): {result}")
    
    def test_invalid_amount():
        print("\nTest 2: Invalid Amount")
        print("=====================")
        payment_system.company_var.set('SALAM')
        payment_system.beneficiary_var.set('Test Beneficiary')
        payment_system.reference_var.set('REF-001')
        payment_system.amount_var.set('invalid')  # Invalid amount
        result = payment_system.validate_payment()
        print(f"Validation result (should be False): {result}")
    
    def test_valid_input():
        print("\nTest 3: Valid Input")
        print("==================")
        payment_system.company_var.set('SALAM')
        payment_system.beneficiary_var.set('Test Beneficiary')
        payment_system.reference_var.set('REF-001')
        payment_system.amount_var.set('1000.00')  # Valid amount
        result = payment_system.validate_payment()
        print(f"Validation result (should be True): {result}")
    
    # Run tests after a short delay
    root.after(500, test_empty_fields)
    root.after(1000, test_invalid_amount)
    root.after(1500, test_valid_input)
    root.after(2000, root.destroy)  # Close after tests
    
    root.mainloop()

if __name__ == '__main__':
    test_validation()
