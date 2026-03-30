from typing import Any
# Inners
from .exceptions import SignatureParameterError


def validate_is_type(value: Any, value_name: str) -> None:
    """
    Validates that the provided value is a type (class).

    Usage:
        - create_copy_signature()       — validates the `return_type` parameter
        - create_keyword_parameter()    — validates the `annotation` parameter
        - create_positional_parameter() — validates the `annotation` parameter

    Raises:
        SignatureParameterError(TypeError): If the value is not a type.
    """
    if not isinstance(value, type):
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = value_name,
            value       = value,
            expected    = "a valid type (class), e.g. int, str, MyClass",
            problem     = f"'{value_name}' must be a type (class), but got {type(value).__name__!r}.",
            how_to_fix  = (
                f"Pass a class as '{value_name}', e.g. return_type=int or return_type=MyClass.",
                "Do not pass instances, strings, or other non-type values.",
                "If no return type is needed, pass None.",
            ),
            get_location = 2,
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_type

## Purpose
Validates that the provided value is a type (class) — an instance of `type`.
Used wherever an annotation or return type is expected to be a plain class.

## When it is called
- `create_copy_signature()`       — `return_type` parameter
- `create_keyword_parameter()`    — `annotation` parameter
- `create_positional_parameter()` — `annotation` parameter

## Notes
- Uses `isinstance(value, type)` — accepts only plain classes (`int`, `str`,
  `MyClass`). Instances, strings, and `None` are rejected.
- `get_location=2` points the error to the caller's call site.
"""