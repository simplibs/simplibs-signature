from .signature import signature
from .signature_copy import signature_copy
from .signature_set import signature_set
from .builders import apply_signature_to_wraps, create_signature_decorator


__all__ = [
    # Decorators
    "signature",
    "signature_copy",
    "signature_set",
    # Builder utilities
    "apply_signature_to_wraps",
    "create_signature_decorator",
]


_DESIGN_NOTES = """
# decorators

## Contents
Decorators for applying custom signatures to functions, and utilities for building
custom decorators.

| Name                        | Type      | Description                                  |
|-----------------------------|-----------|----------------------------------------------|
| `signature`                 | Decorator | Assemble/merge signatures inline             |
| `signature_copy`            | Decorator | Copy and transform existing signature        |
| `signature_set`             | Decorator | Assign a pre-existing signature directly     |
| `apply_signature_to_wraps`  | Utility   | Create wrapper with custom signature         |
| `create_signature_decorator`| Utility   | Build reusable decorator from signature      |
"""