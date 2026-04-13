from .apply_signature_to_wraps import apply_signature_to_wraps
from .create_signature_decorator import create_signature_decorator


__all__ = [
    "apply_signature_to_wraps",
    "create_signature_decorator",
]


_DESIGN_NOTES = """
# decorators/builders

## Contents
Low-level utilities for building custom signature-aware decorators.

| Name                        | Description                                      |
|-----------------------------|--------------------------------------------------|
| `apply_signature_to_wraps`  | Create wrapper with custom signature + async support |
| `create_signature_decorator`| Convert signature into a reusable decorator      |
"""
