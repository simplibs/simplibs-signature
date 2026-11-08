from .raise_duplicate_parameter_error import raise_duplicate_parameter_error
from .raise_invalid_parameter_kind_error import raise_invalid_parameter_kind_error
from .raise_invalid_parameter_order_error import raise_invalid_parameter_order_error


_DESIGN_NOTES = """
# Collector Validations Sub-Package

## Purpose
The errors of the collector, one function per message. Plain imports, no
`__all__`: the package root decides what is public.

## Internal Components Registry

| Component                            | Type     | Description                                        |
| :----------------------------------- | :------- | :------------------------------------------------- |
| `raise_duplicate_parameter_error`    | Function | A name, or a second variadic, is already stored.   |
| `raise_invalid_parameter_kind_error` | Function | A kind the storage map has no slot for.            |
| `raise_invalid_parameter_order_error`| Function | A required positional parameter after an optional. |
"""
