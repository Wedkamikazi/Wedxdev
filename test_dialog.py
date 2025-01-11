import tkinter as tk
from tkinter import ttk
from payment_system_v4 import PaymentSystem
from datetime import datetime

def main():
    root = tk.Tk()
    payment_system = PaymentSystem(root)
    
    # Set test values
    payment_system.company_var.set('SALAM')
    payment_system.beneficiary_var.set('Test Beneficiary')
    payment_system.reference_var.set('TEST-REF-001')
    payment_system.amount_var.set('1000.00')
    payment_system.date_var.set('2025-01-11')
    
    # Process payment after a short delay
    root.after(1000, payment_system.process_payment)
    
    root.mainloop()

if __name__ == '__main__':
    main()
