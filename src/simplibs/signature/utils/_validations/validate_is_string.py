# Inners
from .exceptions import SignatureParameterError


def validate_is_string(value, value_name: str) -> None:
    """
    Validates that the provided value is a string (str).

    Usage:
        - create_positional_parameter() — validates the `name` parameter
        - create_keyword_parameter()    — validates the `name` parameter

    Raises:
        SignatureParameterError(TypeError): If the value is not a str.
    """
    if not isinstance(value, str):
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = value_name,
            value       = value,
            expected    = "a string (str)",
            problem     = f"'{value_name}' must be a string, but got {type(value).__name__!r}.",
            how_to_fix  = (
                f"Pass a string as '{value_name}'.",
                "Example: name='my_parameter'",
                "Do not pass integers, None, or other non-string values.",
            ),
            get_location = 2,
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_string

## Purpose
Validates that the provided value is a string (`str`).
Used wherever a parameter name is expected — parameter names must always
be plain strings.

## When it is called
- `create_positional_parameter()` — `name` parameter
- `create_keyword_parameter()`    — `name` parameter

## Notes
- Uses `isinstance` — rejects integers, `None`, and any other non-string values.
- `get_location=2` points the error to the caller's call site.
"""