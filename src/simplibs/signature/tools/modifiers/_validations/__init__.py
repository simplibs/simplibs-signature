from .raise_signature_structure_value_error import raise_signature_structure_value_error
from .raise_signature_type_error import raise_signature_type_error


_DESIGN_NOTES = """
# Modifiers Validations Sub-Package

## Purpose
The errors of `add_params_to_signature`. Plain imports, no `__all__`: the
package root decides what is public.

## Internal Components Registry

| Component                                | Type     | Description                                  |
| :--------------------------------------- | :------- | :------------------------------------------- |
| `raise_signature_structure_value_error`  | Function | `inspect` refuses the resulting structure.   |
| `raise_signature_type_error`             | Function | An item has an unusable type.                |
"""
