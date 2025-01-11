import tkinter as tk
from payment_system_v4 import PaymentSystem

def main():
    root = tk.Tk()
    app = PaymentSystem(root)
    root.mainloop()

if __name__ == '__main__':
    main()
