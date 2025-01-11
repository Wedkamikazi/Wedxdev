# Payment System Quick Start Guide

## 1. Starting the System 🚀

```bash
cd c:/WedxDev/GGG
python src/payment_system.py
```

## 2. Common Operations

### Processing a New Payment 💸
1. Fill in payment details:
   - Select Company: `SALAM` or `MVNO`
   - Enter Beneficiary Name
   - Enter Reference Number
   - Enter Amount
   - Date (defaults to today)

2. Quick Steps:
   ```
   ➊ Enter Details → ➋ Click Validate → ➌ Click Process → ➍ Confirm
   ```

3. Success Indicators:
   - Green validation message
   - Confirmation dialog
   - Status update in results panel

### Checking Payment Status 🔍
1. Quick Check:
   ```
   Enter Reference Number → Click "Check Status"
   ```

2. Status Types:
   - Under Process
   - Completed
   - Failed
   - Cancelled

### Handling Common Errors ⚠️

#### Invalid Reference
```
Problem: "Invalid Reference Format"
Fix: Ensure reference follows format: XXX-YYYY-NNNN
```

#### Duplicate Payment
```
Problem: "Payment Already Exists"
Fix: Check status of existing payment or use new reference
```

#### Amount Error
```
Problem: "Invalid Amount"
Fix: Enter positive number, use period for decimal
```

## 3. Quick File Access 📁

### View Files
Click buttons at bottom of window:
- `BS-Salam`: SALAM bank statements
- `BS-MVNO`: MVNO bank statements
- `CNP-Salam`: SALAM payments
- `CNP-MVNO`: MVNO payments
- `Treasury`: All payments

### File Locations
```
data/
├── bank_statements/
│   ├── salam/BS_SALAM_CURRENT.csv
│   └── mvno/BS_MVNO_CURRENT.csv
├── cnp/
│   ├── salam/CNP_SALAM_CURRENT.csv
│   └── mvno/CNP_MVNO_CURRENT.csv
└── treasury/TREASURY_CURRENT.csv
```

## 4. Quick Troubleshooting 🔧

### System Won't Start
1. Check Python path:
   ```bash
   python set_python_path.py
   ```
2. Verify files exist in `src/`
3. Check log file in `data/logs/system.log`

### Payment Won't Process
1. Validation:
   - Check all fields filled
   - Verify amount format
   - Ensure unique reference

2. File Access:
   - Check file permissions
   - Verify CSV files exist
   - Look for error in results panel

### Status Check Fails
1. Verify reference number exists
2. Check exception log:
   ```
   data/exceptions/EXCEPTION_LOG.csv
   ```
3. Review audit trail:
   ```
   data/exceptions/AUDIT_LOG.csv
   ```

## 5. Common Tasks Cheat Sheet 📝

### New Payment
```
➊ Company    : Select from dropdown
➋ Beneficiary: Enter name
➌ Reference  : Format XXX-YYYY-NNNN
➍ Amount     : Positive number
➎ Date       : YYYY-MM-DD
```

### Status Check
```
➊ Enter reference in Reference field
➋ Click "Check Status"
➌ View results in panel
```

### View Transactions
```
➊ Click file button (BS/CNP/Treasury)
➋ File opens in default CSV viewer
➌ Latest entries at bottom
```

### Update All Statuses
```
➊ Click "Update All Statuses"
➋ Wait for completion
➌ Check results panel
```

## 6. Keyboard Shortcuts ⌨️

```
Alt + V : Validate Payment
Alt + P : Process Payment
Alt + C : Check Status
Alt + R : Clear Form
F5      : Update All Statuses
```

## 7. Need Help? 🆘

1. Check system log:
   ```
   data/logs/system.log
   ```

2. Review exceptions:
   ```
   data/exceptions/EXCEPTION_LOG.csv
   ```

3. Contact Support:
   - System Admin: [Contact]
   - Tech Support: [Contact]

---
For detailed procedures, see: `OPERATIONAL_PROCEDURES.md`
