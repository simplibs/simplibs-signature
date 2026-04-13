from typing import Any
# Outers
from ..exceptions import SignatureParameterError


def validate_is_string(
    value: Any,
    value_name: str = "name"
) -> None:
    """
    Validates that the provided value is a string (str).

    Args:
        value: The value to verify.
        value_name: The name of the parameter for error messages.

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
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_string

## Purpose
Validates that the provided value is a string (`str`).
Used wherever a parameter name is expected — parameter names must always
be plain strings.

## Where it is used
- `create_positional_parameter()` — validates the `name` argument.
- `create_keyword_parameter()` — validates the `name` argument.

## Validation Method
Simple `isinstance` check — rejects integers, `None`, and any other non-string values.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
- Part of the parameter factory validation pipeline; ensures all parameters
  have properly named arguments before `inspect.Parameter` construction.
"""