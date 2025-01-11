import tkinter as tk
from payment_system_v4 import PaymentSystem

def test_form():
    root = tk.Tk()
    payment_system = PaymentSystem(root)
    
    def verify_initial_state():
        print("\nTest 1: Initial State")
        print("====================")
        print(f"Company: '{payment_system.company_var.get()}'")
        print(f"Beneficiary: '{payment_system.beneficiary_var.get()}'")
        print(f"Reference: '{payment_system.reference_var.get()}'")
        print(f"Amount: '{payment_system.amount_var.get()}'")
        print(f"Date: '{payment_system.date_var.get()}'")
    
    def verify_form_input():
        print("\nTest 2: Form Input")
        print("=================")
        # Set test values
        payment_system.company_var.set('SALAM')
        payment_system.beneficiary_var.set('Test Beneficiary')
        payment_system.reference_var.set('REF-001')
        payment_system.amount_var.set('1000.00')
        
        print("After setting values:")
        print(f"Company: '{payment_system.company_var.get()}'")
        print(f"Beneficiary: '{payment_system.beneficiary_var.get()}'")
        print(f"Reference: '{payment_system.reference_var.get()}'")
        print(f"Amount: '{payment_system.amount_var.get()}'")
    
    def verify_clear():
        print("\nTest 3: Clear Form")
        print("=================")
        payment_system.clear_form()
        print("After clearing form:")
        print(f"Company: '{payment_system.company_var.get()}'")
        print(f"Beneficiary: '{payment_system.beneficiary_var.get()}'")
        print(f"Reference: '{payment_system.reference_var.get()}'")
        print(f"Amount: '{payment_system.amount_var.get()}'")
        print(f"Date: '{payment_system.date_var.get()}'")
    
    # Run tests after a short delay
    root.after(500, verify_initial_state)
    root.after(1000, verify_form_input)
    root.after(1500, verify_clear)
    root.after(2000, root.destroy)  # Close after tests
    
    root.mainloop()

if __name__ == '__main__':
    test_form()
