from .apply_signature_to_wraps import apply_signature_to_wraps
from .create_signature_decorator import create_signature_decorator


_DESIGN_NOTES = """
# signature_decorators/utils

## Contents
Lower-level utilities for building signature-aware decorators.

| Name                        | Description                                                          |
|-----------------------------|----------------------------------------------------------------------|
| `apply_signature_to_wraps`  | Creates a new wrapper around a function with an assigned signature   |
| `create_signature_decorator`| Produces a reusable decorator from an `inspect.Signature`            |
"""