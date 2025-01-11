from datetime import datetime

class ValidationSystem:
    def __init__(self):
        self.threshold_amount = 15000.00
        self.tolerance = 0.01  # 1% tolerance

    def validate_input(self, data):
        """Initial validation of input data"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'messages': []
        }

        # Company validation
        if not data['company']:
            results['valid'] = False
            results['errors'].append("Company selection required")

        # Beneficiary validation
        if not data['beneficiary'].strip():
            results['valid'] = False
            results['errors'].append("Beneficiary name required")

        # Reference validation
        if not self._validate_reference(data['reference']):
            results['valid'] = False
            results['errors'].append("Invalid reference format")

        # Amount validation
        amount_result = self._validate_amount(data['amount'])
        if not amount_result['valid']:
            results['valid'] = False
            results['errors'].append(amount_result['error'])

        # Date validation
        date_result = self._validate_date(data['date'])
        if not date_result['valid']:
            results['valid'] = False
            results['errors'].append(date_result['error'])
        if date_result.get('cnp_required'):
            results['warnings'].append("CNP verification required for old payment")

        return results

    def _validate_reference(self, reference):
        """Validate reference number format"""
        if not reference.strip():
            return False
        # Allow alphanumeric, hyphens, and underscores
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
        return all(c in valid_chars for c in reference.strip())

    def _validate_amount(self, amount):
        """Validate amount and check threshold"""
        result = {'valid': True, 'error': None}
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                result['valid'] = False
                result['error'] = "Amount must be greater than 0"
            elif amount_float > 999999999.99:
                result['valid'] = False
                result['error'] = "Amount exceeds maximum limit"
        except ValueError:
            result['valid'] = False
            result['error'] = "Invalid amount format"
        return result

    def _validate_date(self, date_str):
        """Validate date and check CNP requirement"""
        result = {'valid': True, 'error': None, 'cnp_required': False}
        try:
            payment_date = datetime.strptime(date_str, '%Y-%m-%d')
            current_date = datetime.now()
            
            if payment_date > current_date:
                result['valid'] = False
                result['error'] = "Future date not allowed"
            elif payment_date.year < current_date.year or payment_date.month < current_date.month:
                result['cnp_required'] = True
        except ValueError:
            result['valid'] = False
            result['error'] = "Invalid date format (YYYY-MM-DD)"
        return result

    def cross_reference_check(self, data, file_handler):
        """Perform cross-reference checking across all relevant files"""
        results = {
            'matches': [],
            'warnings': [],
            'messages': []
        }

        # Check relevant files based on company
        if data['company'] == 'SALAM':
            self._check_file('BS-Salam', data, results, file_handler)
            if results.get('cnp_required'):
                self._check_file('CNP-Salam', data, results, file_handler)
        else:  # MVNO
            self._check_file('BS-MVNO', data, results, file_handler)
            if results.get('cnp_required'):
                self._check_file('CNP-MVNO', data, results, file_handler)

        return results

    def _check_file(self, file_type, data, results, file_handler):
        """Check for matches in specific file"""
        try:
            file_data = file_handler.read_file(file_type)
            for record in file_data:
                if self._is_matching_record(record, data):
                    match = {
                        'file': file_type,
                        'reference': record['reference'],
                        'amount': record['amount'],
                        'date': record['date']
                    }
                    results['matches'].append(match)
        except Exception as e:
            results['warnings'].append(f"Error checking {file_type}: {str(e)}")

    def _is_matching_record(self, record, data):
        """Check if record matches the input data"""
        # Reference match
        if record['reference'].strip() == data['reference'].strip():
            # For amounts > 15000, allow 1% tolerance
            amount = float(record['amount'])
            input_amount = float(data['amount'])
            
            if amount > self.threshold_amount:
                difference = abs(amount - input_amount) / amount
                return difference <= self.tolerance
            else:
                return amount == input_amount
        return False
