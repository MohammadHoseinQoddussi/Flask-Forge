from typing import Any, Dict, Optional, Type

from .exceptions import MissingDataError


class Form:
    """Form validation class with support for data, type, length, and number validation."""

    def __init__(self, form: Optional[Dict[str, Any]] = None):
        self.form = form if form is not None else {}
        self._reset_errors()

    def _reset_errors(self):
        self.type_errors: Dict[str, str] = {}
        self.data_errors: Dict[str, str] = {}
        self.length_errors: Dict[str, str] = {}
        self.number_errors: Dict[str, str] = {}

    def check_data(self, *datas: str) -> None:
        for data in datas:
            if data not in self.form:
                self.data_errors[data] = f'the {data} is not defined'

    def check_type(self, **KT: Dict[str, Type]) -> None:
        for key, expected_type in KT.items():
            if key not in self.form:
                self.type_errors[key] = f'KeyError: the {key} is not in the form'
            elif not isinstance(self.form[key], expected_type):
                self.type_errors[key] = f'the {key} type is not {expected_type.__name__}'

    def check_length(self, **KT: Dict[str, Dict[str, int]]) -> None:
        for key, constraints in KT.items():
            if key not in self.form:
                continue
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
        for key, constraints in KT.items():
            if key not in self.form:
                continue
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

    def validate(self, minimum: dict = None, maximum: dict = None, types: dict = None, datas: tuple = None) -> bool:
        if datas is None or types is None or minimum is None or maximum is None:
            raise MissingDataError('the data or type or minimum or maximum is not defined')

        self._reset_errors()
        self.check_data(*datas)
        self.check_type(**types)

        for key in self.form.keys():
            if isinstance(self.form[key], (int, float)):
                self.check_number(**{key: {'min': minimum.get('number'), 'max': maximum.get('number')}})
            elif isinstance(self.form[key], str):
                self.check_length(**{key: {'min': minimum.get('string'), 'max': maximum.get('string')}})
        return self.is_valid()

    def is_valid(self) -> bool:
        return not any([
            self.data_errors,
            self.type_errors,
            self.length_errors,
            self.number_errors,
        ])

    def get_errors(self):
        return {
            'data_errors': self.data_errors,
            'type_errors': self.type_errors,
            'length_errors': self.length_errors,
            'number_errors': self.number_errors,
        }

    def get_form(self):
        return self.form
