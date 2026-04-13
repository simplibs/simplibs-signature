from .validate_is_bool import validate_is_bool
from .validate_is_callable import validate_is_callable
from .validate_is_string import validate_is_string


__all__ = [
    "validate_is_bool",
    "validate_is_callable",
    "validate_is_string",
]


_DESIGN_NOTES = """
# core/validators/_primitives

## Contents
Basic type validation functions. These are reusable across the library.

| Name                   | Description                                    |
|------------------------|------------------------------------------------|
| `validate_is_bool`     | Validates that a value is a boolean            |
| `validate_is_callable` | Validates that a value can be called           |
| `validate_is_string`   | Validates that a value is a string             |
"""