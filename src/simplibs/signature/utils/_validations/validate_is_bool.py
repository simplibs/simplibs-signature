# Inners
from .exceptions import SignatureParameterError


def validate_is_bool(value, value_name: str) -> None:
    """
    Validates that the provided value is of type bool.

    Usage:
        - SignatureCreator.__init__()  — validates the `base_func_first` parameter
        - ParameterCollector.__init__() — validates the `accept_double` parameter

    Raises:
        SignatureParameterError(TypeError): If the value is not a bool.
    """
    if not isinstance(value, bool):
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = value_name,
            value       = value,
            expected    = "a boolean value: True or False",
            problem     = f"'{value_name}' must be a bool, but got {type(value).__name__!r}.",
            how_to_fix  = (
                f"Pass a boolean value: {value_name}=True or {value_name}=False.",
                "Do not pass strings ('true'), integers (1/0) or other non-bool values.",
            ),
            get_location = 2,
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_bool

## Purpose
Validates that the provided value is a bool — used wherever a parameter
must be strictly True or False, with no implicit conversion.

## When it is called
- `SignatureCreator.__init__()` — `base_func_first` parameter
- `ParameterCollector.__init__()` — `accept_double` parameter

## Notes
- Uses `isinstance` — integers (1/0) and strings ('true') do not pass.
- `get_location=2` points the error to the caller's call site.
"""