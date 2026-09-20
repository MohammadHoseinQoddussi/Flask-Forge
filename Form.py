from exceptions import MissingDataError
from typing import Dict, Any, Type, Optional, List, Tuple

class Form:
    """Form validation class with support for data, type, length, and number validation."""
    
    #==============init==============
    def __init__(self, form: Optional[Dict[str, Any]] = None):
        self.form = form if form is not None else {}
        self._reset_errors()
    
    def _reset_errors(self):
        """Reset all error dictionaries to empty."""
        self.type_errors: Dict[str, str] = {}
        self.data_errors: Dict[str, str] = {}
        self.length_errors: Dict[str, str] = {}
        self.number_errors: Dict[str, str] = {}

    def check_data(self, *datas: str) -> None:
        """Check if required fields exist in the form."""
        for data in datas:
            if data not in self.form:
                self.data_errors[data] = f'the {data} is not defined'

    def check_type(self, **KT: Dict[str, Type]) -> None:
        """Check if field values match expected types."""
        for key, expected_type in KT.items():
            if key not in self.form:
                self.type_errors[key] = f'KeyError: the {key} is not in the form'
            elif not isinstance(self.form[key], expected_type):
                self.type_errors[key] = f'the {key} type is not {expected_type.__name__}'

    def check_length(self, **KT: Dict[str, Dict[str, int]]) -> None:
        """Check string length constraints."""
        for key, constraints in KT.items():
            if key not in self.form:
                continue  # Skip if key doesn't exist (handled by check_data)
            
            min_len = constraints.get('min', 0)
            max_len = constraints.get('max', float('inf'))
            
            if min_len > max_len:
                raise MissingDataError('the min is bigger than the max')
            
            value = self.form[key]
            if not isinstance(value, (str, list, tuple)):
                self.length_errors[key] = f'the {key} is not a sequence type'
                continue
                
            actual_len = len(value)
            if actual_len < min_len or actual_len > max_len:
                self.length_errors[key] = f'the {key} length is not between {min_len} and {max_len}'

    def check_number(self, **KT: Dict[str, Dict[str, float]]) -> None:
        """Check numeric value constraints."""
        for key, constraints in KT.items():
            if key not in self.form:
                continue  # Skip if key doesn't exist (handled by check_data)
            
            min_val = constraints.get('min', float('-inf'))
            max_val = constraints.get('max', float('inf'))
            
            if min_val > max_val:
                raise MissingDataError('the min is bigger than the max')
            
            try:
                numeric_value = float(self.form[key])
            except (ValueError, TypeError):
                self.number_errors[key] = f'the {key} is not a valid number'
                continue
            
            if numeric_value < min_val or numeric_value > max_val:
                self.number_errors[key] = f'the {key} value is not between {min_val} and {max_val}'

    def validate(self, minimum:dict=None, maximum:dict=None, types:dict=None, datas:tuple=None) -> bool:
        """
        Validate the form data.
        
        Args:
            minimum: Dict with 'string' and 'number' min constraints
            maximum: Dict with 'string' and 'number' max constraints
            types: Dict mapping field names to expected types
            datas: Tuple of required field names
        
        Returns:
            bool: True if valid, False otherwise
        """
        if datas is None or types is None or minimum is None or maximum is None:
            raise MissingDataError(
                'the data or type or minimum or maximum is not defined'
            )
        
        # Reset errors before validation
        self._reset_errors()
        
        # Run all checks
        self.check_data(*datas)
        self.check_type(**types)
        
        for key in self.form.keys():
            if isinstance(self.form[key], (int, float)):
                self.check_number(
                    **{
                        key: {
                            'min': minimum.get('number'),
                            'max': maximum.get('number')
                        }
                    }
                )
            elif isinstance(self.form[key], str):
                self.check_length(
                    **{
                        key: {
                            'min': minimum.get('string'),
                            'max': maximum.get('string')
                        }
                    }
                )
        
        return self.is_valid()
    
    def is_valid(self) -> bool:
        """Check if the form has no validation errors."""
        return not any([
            self.data_errors,
            self.type_errors,
            self.length_errors,
            self.number_errors
        ])
    
    def get_errors(self) -> Dict[str, Dict[str, str]]:
        """Return all error dictionaries."""
        return {
            'data_errors': self.data_errors,
            'type_errors': self.type_errors,
            'length_errors': self.length_errors,
            'number_errors': self.number_errors
        }
    
    def get_form(self) -> Dict[str, Any]:
        """Return the form data."""
        return self.form