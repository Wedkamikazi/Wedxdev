import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os
from validation_system import ValidationSystem
from file_operations import FileOperations
from status_tracker import StatusTracker
from exception_handler import ExceptionHandler
from audit_trail import AuditTrail

class PaymentSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Payment Processing System - ACTIVE")
        self.root.geometry("800x600")
        
        # Initialize Components
        self.validator = ValidationSystem()
        self.file_ops = FileOperations()
        self.status_tracker = StatusTracker()
        self.exception_handler = ExceptionHandler()
        self.audit_trail = AuditTrail()
        
        # Setup Variables
        self.setup_variables()
        # Create UI
        self.create_layout()
        
        # System startup log
        self.log_audit("System_Start", "Payment system initialized and ready", status='Active')

    def setup_variables(self):
        """Initialize system variables"""
        self.company_var = tk.StringVar()
        self.beneficiary_var = tk.StringVar()
        self.reference_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.exception_var = tk.BooleanVar()
        self.exception_reason = tk.StringVar()
        self.approver_var = tk.StringVar()

    def create_layout(self):
        """Create main application layout"""
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # Create sections
        self.create_payment_section(main_container)
        self.create_results_section(main_container)
        self.create_file_section(main_container)

    def create_payment_section(self, parent):
        """Create payment details section"""
        payment_frame = ttk.LabelFrame(parent, text="Payment Details", padding="10")
        payment_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        payment_frame.grid_columnconfigure(1, weight=1)

        # Company Selection
        ttk.Label(payment_frame, text="Company:").grid(row=0, column=0, sticky="w", pady=5)
        company_combo = ttk.Combobox(payment_frame, textvariable=self.company_var)
        company_combo['values'] = ('SALAM', 'MVNO')
        company_combo.grid(row=0, column=1, sticky="ew", pady=5)
        company_combo.state(['readonly'])

        # Beneficiary
        ttk.Label(payment_frame, text="Beneficiary:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(payment_frame, textvariable=self.beneficiary_var).grid(row=1, column=1, sticky="ew", pady=5)

        # Reference
        ttk.Label(payment_frame, text="Reference:").grid(row=2, column=0, sticky="w", pady=5)
        ref_frame = ttk.Frame(payment_frame)
        ref_frame.grid(row=2, column=1, sticky="ew", pady=5)
        ref_frame.grid_columnconfigure(0, weight=1)
        ttk.Entry(ref_frame, textvariable=self.reference_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(ref_frame, text="Check Status", command=self.check_status).grid(row=0, column=1, padx=(5, 0))

        # Amount
        ttk.Label(payment_frame, text="Amount:").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Entry(payment_frame, textvariable=self.amount_var).grid(row=3, column=1, sticky="ew", pady=5)

        # Date
        ttk.Label(payment_frame, text="Date:").grid(row=4, column=0, sticky="w", pady=5)
        self.date_entry = ttk.Entry(payment_frame, textvariable=self.date_var)
        self.date_entry.grid(row=4, column=1, sticky="ew", pady=5)

        # Exception checkbox for old payments
        self.exception_check = ttk.Checkbutton(
            payment_frame,
            text="Process as Exception (for old payments)",
            variable=self.exception_var,
            command=self.toggle_exception_mode
        )
        self.exception_check.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Exception reason (hidden by default)
        self.exception_frame = ttk.Frame(payment_frame)
        self.exception_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.exception_frame.grid_remove()

        ttk.Label(self.exception_frame, text="Reason for Exception:").pack(fill="x", pady=(0, 5))
        self.exception_reason_entry = tk.Text(self.exception_frame, height=3)
        self.exception_reason_entry.pack(fill="x")

        ttk.Label(self.exception_frame, text="Approver's Name:").pack(fill="x", pady=(5, 0))
        self.approver_entry = ttk.Entry(self.exception_frame, textvariable=self.approver_var)
        self.approver_entry.pack(fill="x", pady=(0, 5))

        # Missing CNP Explanation Frame (hidden by default)
        self.cnp_explanation_frame = ttk.LabelFrame(payment_frame, text="Missing CNP Explanation")
        self.cnp_explanation_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.cnp_explanation_frame.grid_remove()
        
        ttk.Label(self.cnp_explanation_frame, text="Explanation for Missing CNP Entry:").pack(fill="x", pady=(5, 0))
        self.cnp_explanation = tk.Text(self.cnp_explanation_frame, height=3)
        self.cnp_explanation.pack(fill="x", pady=5)
        
        ttk.Label(self.cnp_explanation_frame, text="Approver's Name:").pack(fill="x")
        self.cnp_approver = ttk.Entry(self.cnp_explanation_frame)
        self.cnp_approver.pack(fill="x", pady=(0, 5))
        
        ttk.Label(self.cnp_explanation_frame, text="Signature Declaration:").pack(fill="x")
        self.cnp_signature = ttk.Entry(self.cnp_explanation_frame)
        self.cnp_signature.pack(fill="x", pady=(0, 5))

        # Warning label for missing CNP
        self.warning_label = ttk.Label(payment_frame, text="Warning: Payment requires CNP explanation", foreground="red")
        self.warning_label.grid(row=8, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.warning_label.grid_remove()

        # Buttons
        button_frame = ttk.Frame(payment_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Validate", command=self.validate_payment).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Process", command=self.process_payment).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side="left", padx=5)

    def create_results_section(self, parent):
        """Create results display section"""
        results_frame = ttk.LabelFrame(parent, text="Results", padding="10")
        results_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)

        # Results Text
        self.results_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky="nsew")
        self.results_text.config(state='disabled')

        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_text['yscrollcommand'] = scrollbar.set

    def create_file_section(self, parent):
        """Create file access section"""
        file_frame = ttk.LabelFrame(parent, text="File Access", padding="10")
        file_frame.grid(row=2, column=0, sticky="ew")

        # File buttons
        ttk.Button(file_frame, text="BS-Salam", command=lambda: self.open_file("BS-Salam")).grid(row=0, column=0, padx=5)
        ttk.Button(file_frame, text="BS-MVNO", command=lambda: self.open_file("BS-MVNO")).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="CNP-Salam", command=lambda: self.open_file("CNP-Salam")).grid(row=0, column=2, padx=5)
        ttk.Button(file_frame, text="CNP-MVNO", command=lambda: self.open_file("CNP-MVNO")).grid(row=0, column=3, padx=5)
        ttk.Button(file_frame, text="Treasury", command=lambda: self.open_file("Treasury")).grid(row=0, column=4, padx=5)

        # Update Status button
        ttk.Button(file_frame, text="Update All Statuses", command=self.update_all_statuses).grid(
            row=1, column=0, columnspan=5, pady=10)

    def validate_payment(self):
        """Validate payment details"""
        try:
            # Get form data
            reference = self.reference_var.get().strip()
            amount = self.amount_var.get().strip()
            date_str = self.date_var.get().strip()
            company = self.company_var.get()
            
            if not all([reference, amount, date_str, company]):
                raise ValueError("All fields are required")
                
            # Check old payment requirements first
            if not self.check_old_payment_requirements():
                return False
            
            # Parse date
            payment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            
            is_old_payment = (
                payment_date.year < current_date.year or 
                (payment_date.year == current_date.year and payment_date.month < current_date.month)
            )
            
            if is_old_payment and not self.exception_var.get():
                # Require explanation and approval for missing verifications
                explanation = self.cnp_explanation.get("1.0", "end-1c").strip()
                approver = self.cnp_approver.get().strip()
                signature = self.cnp_signature.get().strip()
                
                if not all([explanation, approver, signature]):
                    raise ValueError(
                        "For old payments missing verification:\n"
                        "- Explanation is required\n"
                        "- Approver's name is required\n"
                        "- Signature declaration is required"
                    )
            
            self.show_in_results("✅ Validation successful!", "success")
            return True
            
        except Exception as e:
            self.show_in_results(f"❌ Validation failed: {str(e)}", "error")
            return False
            
    def process_payment(self):
        """Process the payment"""
        if not self.validate_payment():
            return
            
        try:
            # Get form data
            payment_data = {
                'reference': self.reference_var.get().strip(),
                'amount': self.amount_var.get().strip(),
                'date': self.date_var.get().strip(),
                'company': self.company_var.get(),
                'beneficiary': self.beneficiary_var.get().strip(),
                'status': 'Under Process',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Add CNP explanation if provided
            if not self.exception_var.get() and self.cnp_explanation_frame.winfo_viewable():
                payment_data['cnp_explanation'] = self.cnp_explanation.get("1.0", "end-1c").strip()
                payment_data['cnp_approver'] = self.cnp_approver.get().strip()
                payment_data['cnp_signature'] = self.cnp_signature.get().strip()
            
            # Show confirmation dialog
            confirm_msg = f"Please confirm payment details:\n\n"
            confirm_msg += f"Reference: {payment_data['reference']}\n"
            confirm_msg += f"Amount: {payment_data['amount']}\n"
            confirm_msg += f"Date: {payment_data['date']}\n"
            confirm_msg += f"Company: {payment_data['company']}\n"
            confirm_msg += f"Beneficiary: {payment_data['beneficiary']}\n"
            
            if self.exception_var.get():
                confirm_msg += f"\n🚨 WARNING: EXCEPTION MODE ACTIVE\n"
                confirm_msg += f"This payment will bypass CNP validation!\n"
            elif 'cnp_explanation' in payment_data:
                confirm_msg += f"\n⚠️ OLD PAYMENT - CNP EXPLANATION:\n"
                confirm_msg += f"Reason: {payment_data['cnp_explanation']}\n"
                confirm_msg += f"Approved by: {payment_data['cnp_approver']}\n"
                confirm_msg += f"Signature: {payment_data['cnp_signature']}\n"
            
            if not messagebox.askyesno("Confirm Payment", confirm_msg):
                self.show_in_results("Payment cancelled by user", "info")
                return
            
            # Save to Treasury
            self.save_to_treasury(payment_data)
            
            # If it's an old payment, save to CNP unless in exception mode
            payment_date = datetime.strptime(payment_data['date'], '%Y-%m-%d').date()
            current_date = datetime.now().date()
            is_old_payment = (
                payment_date.year < current_date.year or 
                (payment_date.year == current_date.year and payment_date.month < current_date.month)
            )
            
            if is_old_payment and not self.exception_var.get():
                self.save_to_cnp(payment_data)
            
            self.show_in_results("✅ Payment processed successfully!", "success")
            self.clear_form()
            
        except Exception as e:
            self.show_in_results(f"❌ Error processing payment: {str(e)}", "error")

    def get_payment_data(self):
        """Get current payment data from form"""
        payment_data = {
            'company': self.company_var.get(),
            'beneficiary': self.beneficiary_var.get(),
            'reference': self.reference_var.get().strip(),
            'amount': self.amount_var.get(),
            'date': self.date_var.get(),
            'status': 'Under Process',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # For old payments, add exception details
        if self.exception_var.get():
            payment_data['exception_reason'] = self.exception_reason_entry.get("1.0", "end-1c").strip()
            payment_data['exception_approver'] = self.approver_var.get().strip()

        return payment_data

    def confirm_payment(self, payment_data):
        """Show confirmation dialog"""
        message = f"""Please confirm payment details:

Company: {payment_data['company']}
Beneficiary: {payment_data['beneficiary']}
Reference: {payment_data['reference']}
Amount: {payment_data['amount']}
Date: {payment_data['date']}

Do you want to proceed with this payment?"""

        if self.exception_var.get():
            message += f"\n\n⚠️ EXCEPTION PROCESSING:\n"
            message += f"Reason: {payment_data['exception_reason']}\n"
            message += f"Approved by: {payment_data['exception_approver']}\n"

        self.log_audit('Payment_Confirmation', 'Showing confirmation dialog', payment_data['reference'], 'Started')
        result = messagebox.askyesno("Confirm Payment", message)
        self.log_audit('Payment_Confirmation', f'User {"confirmed" if result else "cancelled"} payment', payment_data['reference'], 'Completed')

        if not result:
            self.show_in_results("\nPayment cancelled by user")

        return result

    def check_status(self):
        """Check payment status"""
        reference = self.reference_var.get().strip()
        if not reference:
            self.show_in_results("Please enter a reference number")
            return

        try:
            self.log_audit('Status_Check', 'Checking payment status', reference, 'Started')

            status_data = self.status_tracker.update_status(reference)
            exceptions = self.exception_handler.get_open_exceptions(reference)

            self.display_status_results(status_data, exceptions)

            self.log_audit('Status_Check', 
                          f"Status: {status_data['status']}",
                          reference,
                          'Completed')

        except Exception as e:
            self.handle_exception('Status_Check_Error', str(e), reference)

    def update_all_statuses(self):
        """Update status for all payments"""
        try:
            results = self.status_tracker.update_all_statuses()

            # Format results nicely
            output = "\n=== Updating All Statuses ===\n\n"

            if results['updated'] > 0:
                output += f"Successfully updated {results['updated']} payment(s)\n\n"
                for detail in results['details']:
                    output += f"• {detail}\n"
            else:
                output += "No payments needed updating\n"

            if results['errors'] > 0:
                output += f"\nEncountered {results['errors']} error(s):\n"
                for detail in results['details']:
                    if 'Error' in detail:
                        output += f"• {detail}\n"

            self.show_in_results(output)

        except Exception as e:
            self.handle_exception('Bulk_Update_Error', str(e))

    def clear_form(self):
        """Clear all form fields"""
        self.company_var.set('')
        self.beneficiary_var.set('')
        self.reference_var.set('')
        self.amount_var.set('')
        self.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.exception_var.set(False)
        self.exception_reason_entry.delete("1.0", "end")
        self.approver_var.set('')

    def show_in_results(self, text, append=False, clear=False):
        """Display text in results panel"""
        self.results_text.config(state='normal')
        if clear:
            self.results_text.delete(1.0, tk.END)
        if append:
            self.results_text.insert(tk.END, text)
        else:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
        self.results_text.config(state='disabled')

    def handle_exception(self, error_type, description, reference=None):
        """Handle system exceptions"""
        exception_data = {
            'reference': reference or self.reference_var.get().strip() or 'N/A',
            'type': error_type,
            'description': description
        }

        exception_result = self.exception_handler.log_exception(exception_data)

        self.show_in_results(
            f"\n=== Exception Logged ===\n\n"
            f"Type: {error_type}\n"
            f"Description: {description}\n"
            f"Reference: {exception_data['reference']}\n"
            f"Time: {exception_result['timestamp']}\n",
            append=True
        )

    def log_audit(self, action, details, reference=None, status='Completed'):
        """Log audit trail"""
        audit_data = {
            'action': action,
            'reference': reference or self.reference_var.get().strip() or 'N/A',
            'details': details,
            'status': status
        }

        return self.audit_trail.log_action(audit_data)

    def open_file(self, file_type):
        """Open file in system default application"""
        try:
            # Convert file type to match the keys in file_ops
            if file_type == "BS-Salam":
                file_type = "BS-SALAM"
            elif file_type == "CNP-Salam":
                file_type = "CNP-SALAM"

            file_path = self.file_ops.get_file_path(file_type)
            if not file_path:
                raise ValueError(f"Invalid file type: {file_type}")

            if not os.path.exists(file_path):
                self.create_empty_file(file_path)

            os.startfile(file_path)
            self.log_audit('File_Access', f"Opened {file_type} file")

        except Exception as e:
            self.handle_exception('File_Access_Error', str(e))

    def create_empty_file(self, file_path):
        """Create new file with headers"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        headers = ['reference', 'amount', 'date', 'status', 'timestamp']
        with open(file_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

    def truncate_text(self, text, max_length=1000):
        """Truncate text to maximum length while preserving meaning"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    def display_validation_results(self, validation_result):
        """Display validation results in the results panel"""
        output = "\n=== Validation Results ===\n\n"
        output += f"Status: {'Valid' if validation_result['valid'] else 'Invalid'}\n\n"

        if validation_result['errors']:
            output += "Errors:\n"
            for error in validation_result['errors'][:10]:  # Limit to first 10 errors
                output += f"- {self.truncate_text(error)}\n"
            if len(validation_result['errors']) > 10:
                output += f"... and {len(validation_result['errors']) - 10} more errors\n"
            output += "\n"

        if validation_result['warnings']:
            output += "Warnings:\n"
            for warning in validation_result['warnings'][:10]:  # Limit to first 10 warnings
                output += f"- {self.truncate_text(warning)}\n"
            if len(validation_result['warnings']) > 10:
                output += f"... and {len(validation_result['warnings']) - 10} more warnings\n"

        self.show_in_results(output)

    def display_verification_results(self, verification_result):
        """Display verification results in the results panel"""
        output = "\n=== Verification Results ===\n\n"
        output += f"Status: {'Matches found' if verification_result['matches'] else 'No matches found'}\n\n"

        if verification_result['details']:
            output += "Details:\n"
            for detail in verification_result['details'][:10]:  # Limit to first 10 details
                output += f"- {self.truncate_text(detail)}\n"
            if len(verification_result['details']) > 10:
                output += f"... and {len(verification_result['details']) - 10} more details\n"
            output += "\n"

        if verification_result['files']:
            output += "Files Checked:\n"
            for file in verification_result['files'][:10]:  # Limit to first 10 files
                output += f"- {self.truncate_text(file)}\n"
            if len(verification_result['files']) > 10:
                output += f"... and {len(verification_result['files']) - 10} more files\n"

        self.show_in_results(output)

    def display_status_results(self, status_data, exceptions):
        """Display payment status and exceptions in the results panel"""
        output = "\n=== Payment Status ===\n\n"
        output += f"Status: {self.truncate_text(status_data['status'])}\n"
        output += f"Last Updated: {status_data['timestamp']}\n"

        if 'details' in status_data:
            output += f"Details: {self.truncate_text(status_data['details'])}\n"

        if exceptions:
            output += "\nExceptions:\n"
            for exception in exceptions[:10]:  # Limit to first 10 exceptions
                output += f"- [{exception['type']}] {self.truncate_text(exception['description'])}\n"
                output += f"  Time: {exception['timestamp']}\n"
            if len(exceptions) > 10:
                output += f"... and {len(exceptions) - 10} more exceptions\n"

        self.show_in_results(output)

    def show_success_message(self):
        """Show success message dialog"""
        messagebox.showinfo("Success", "Payment processed successfully!")

    def save_payment(self, payment_data):
        """Save the payment data to Treasury only"""
        try:
            success, message = self.file_ops.save_payment(payment_data)

            if success:
                self.show_in_results("\nPayment added to Treasury with 'Under Process' status")
                self.show_in_results("\nIMPORTANT: Please process the payment manually in the bank.")
                self.show_in_results("After bank approval, download the bank statement and manually update it.")
                self.show_in_results("Then use 'Update All Statuses' to match and update the Treasury status.")

                # Log the audit
                self.log_audit('Payment_Saved', 
                             f"Payment saved to Treasury: {payment_data['reference']} - {payment_data['beneficiary']}",
                             payment_data['reference'],
                             'Success')
                return True
            else:
                self.handle_exception('Save_Error', message, payment_data['reference'])
                return False
        except Exception as e:
            self.handle_exception('Save_Error', str(e), payment_data['reference'])
            return False

    def save_to_treasury(self, payment_data):
        """Save payment data to treasury file"""
        try:
            treasury_file = os.path.join(
                os.path.dirname(__file__),
                'data',
                'treasury',
                'TREASURY_CURRENT.csv'
            )
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(treasury_file), exist_ok=True)
            
            # Check if file exists and create with headers if it doesn't
            if not os.path.exists(treasury_file):
                with open(treasury_file, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary'])
            
            # Append payment data
            with open(treasury_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    payment_data['reference'],
                    payment_data['amount'],
                    payment_data['date'],
                    payment_data['status'],
                    payment_data['timestamp'],
                    payment_data['company'],
                    payment_data['beneficiary']
                ])
                
        except Exception as e:
            raise Exception(f"Error saving to treasury: {str(e)}")
            
    def save_to_cnp(self, payment_data):
        """Save payment data to CNP file"""
        try:
            cnp_file = os.path.join(
                os.path.dirname(__file__),
                'data',
                'cnp',
                f"CNP_{payment_data['company']}_CURRENT.csv"
            )
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(cnp_file), exist_ok=True)
            
            # Check if file exists and create with headers if it doesn't
            if not os.path.exists(cnp_file):
                with open(cnp_file, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['reference', 'amount', 'date', 'status', 'timestamp', 'company', 'beneficiary', 'explanation', 'approver', 'signature'])
            
            # Append payment data
            with open(cnp_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    payment_data['reference'],
                    payment_data['amount'],
                    payment_data['date'],
                    payment_data['status'],
                    payment_data['timestamp'],
                    payment_data['company'],
                    payment_data['beneficiary'],
                    payment_data.get('cnp_explanation', ''),
                    payment_data.get('cnp_approver', ''),
                    payment_data.get('cnp_signature', '')
                ])
                
        except Exception as e:
            raise Exception(f"Error saving to CNP: {str(e)}")

    def toggle_exception_mode(self):
        """Toggle exception mode for old payments"""
        self.exception_frame.grid_remove() if not self.exception_var.get() else self.exception_frame.grid()
        self.cnp_explanation_frame.grid_remove() if not self.exception_var.get() else self.cnp_explanation_frame.grid()

    def check_old_payment_requirements(self):
        """Check requirements for old payments"""
        reference = self.reference_var.get().strip()
        company = self.company_var.get()
        date_str = self.date_var.get().strip()
        
        try:
            payment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            
            is_old_payment = (
                payment_date.year < current_date.year or 
                (payment_date.year == current_date.year and payment_date.month < current_date.month)
            )
            
            if is_old_payment and not self.exception_var.get():
                # Verify in both CNP and Bank Statement
                verification = self.exception_handler.verify_old_payment({
                    'reference': reference,
                    'company': company
                })
                
                if verification['requires_approval']:
                    # Show warning and explanation requirements
                    warning_text = "⚠️ Old Payment Verification Required:\n"
                    for warning in verification['warnings']:
                        warning_text += f"- {warning}\n"
                    warning_text += "\nPlease provide explanation and approval details."
                    
                    self.warning_label.config(text=warning_text)
                    self.warning_label.grid()
                    self.cnp_explanation_frame.grid()
                    
                    # Update explanation frame label to reflect all missing verifications
                    missing_docs = []
                    if not verification['cnp_verified']:
                        missing_docs.append("CNP")
                    if not verification['bs_verified']:
                        missing_docs.append("Bank Statement")
                    
                    self.cnp_explanation_frame.config(
                        text=f"Missing {' and '.join(missing_docs)} Explanation"
                    )
                    
                    return False
                else:
                    self.warning_label.grid_remove()
                    self.cnp_explanation_frame.grid_remove()
            else:
                self.warning_label.grid_remove()
                self.cnp_explanation_frame.grid_remove()
                
            return True
            
        except ValueError as e:
            self.show_in_results(f"❌ Date validation error: {str(e)}", "error")
            return False

    def check_cnp_requirement(self):
        """Check if payment requires CNP explanation"""
        try:
            date_str = self.date_entry.get().strip()
            if not date_str:
                return
                
            payment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            current_date = datetime.now().date()
            
            # Check if payment is from previous month
            is_old_payment = (
                payment_date.year < current_date.year or 
                (payment_date.year == current_date.year and payment_date.month < current_date.month)
            )
            
            if is_old_payment and not self.exception_var.get():
                # Check if payment exists in CNP
                reference = self.reference_var.get().strip()
                company = self.company_var.get()
                
                if not self.check_cnp_exists(reference, company):
                    self.warning_label.grid()
                    self.cnp_explanation_frame.grid()
                else:
                    self.warning_label.grid_remove()
                    self.cnp_explanation_frame.grid_remove()
            else:
                self.warning_label.grid_remove()
                self.cnp_explanation_frame.grid_remove()
                
        except Exception as e:
            print(f"Error checking CNP requirement: {e}")
            
    def check_cnp_exists(self, reference, company):
        """Check if payment exists in CNP file"""
        if not reference or not company:
            return False
            
        cnp_file = os.path.join(
            os.path.dirname(__file__),
            'data',
            'cnp',
            f'CNP_{company}_CURRENT.csv'
        )
        
        if not os.path.exists(cnp_file):
            return False
            
        try:
            with open(cnp_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['reference'].strip() == reference:
                        return True
        except Exception as e:
            print(f"Error checking CNP file: {e}")
            
        return False

def main():
    try:
        root = tk.Tk()
        app = PaymentSystem(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", str(e))
        raise

if __name__ == "__main__":
    main()
