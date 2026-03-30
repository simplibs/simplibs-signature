import inspect
# Inners
from .exceptions import SignatureParameterError


def validate_is_inspect_signature(value, value_name: str) -> None:
    """
    Validates that the provided value is an instance of inspect.Signature.

    Usage:
        - apply_signature_to_wraps() — validates the `signature` parameter
        - set_signature() — validates the `signature` parameter

    Raises:
        SignatureParameterError(TypeError): If the value is not an inspect.Signature.
    """
    if not isinstance(value, inspect.Signature):
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = value_name,
            value       = value,
            expected    = "an instance of inspect.Signature",
            problem     = f"'{value_name}' must be inspect.Signature, but got {type(value).__name__!r}.",
            how_to_fix  = (
                f"Pass a valid inspect.Signature object as '{value_name}'.",
                "You can obtain one via: inspect.signature(my_func).",
                "Or use SignatureCreator(...).signature from this library.",
            ),
            get_location = 2,
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_inspect_signature

## Purpose
Validates that the provided value is an `inspect.Signature` instance.
Used in `apply_signature_to_wraps()` to guard the `signature` parameter
before it is applied to a wrapped function.

## When it is called
- `apply_signature_to_wraps()` — `signature` parameter

## Notes
- Uses `isinstance` — rejects anything that is not a proper `inspect.Signature`.
- `get_location=2` points the error to the caller's call site.
"""