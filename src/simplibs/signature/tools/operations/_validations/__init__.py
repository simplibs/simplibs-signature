from .raise_signature_composition_attribute_error import raise_signature_composition_attribute_error
from .raise_signature_composition_type_error import raise_signature_composition_type_error
from .raise_signature_composition_value_error import raise_signature_composition_value_error
from .raise_signature_introspection_type_error import raise_signature_introspection_type_error
from .raise_signature_introspection_value_error import raise_signature_introspection_value_error


_DESIGN_NOTES = """
# Operations Validations Sub-Package

## Purpose
The errors of `get_signature` and `compose_signature`, one function per
message. Plain imports, no `__all__`: the package root decides what is public.

## Internal Components Registry

| Component                                     | Type     | Description                                    |
| :-------------------------------------------- | :------- | :--------------------------------------------- |
| `raise_signature_composition_attribute_error` | Function | An item is not a parameter.                    |
| `raise_signature_composition_type_error`      | Function | Input or annotation of an unusable type.       |
| `raise_signature_composition_value_error`     | Function | The parameters do not form a valid signature.  |
| `raise_signature_introspection_type_error`    | Function | An object `inspect.signature` does not support.|
| `raise_signature_introspection_value_error`   | Function | A callable without readable signature metadata.|
"""
