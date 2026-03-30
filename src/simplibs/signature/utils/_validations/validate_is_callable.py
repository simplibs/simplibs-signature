# Inners
from .exceptions import SignatureParameterError


def validate_is_callable(value, value_name: str) -> None:
    """
    Validates that the provided value is callable (a function or callable object).

    Usage:
        - SignatureCreator.__init__()    — validates the `base_func_first` parameter
        - get_signature()                — validates the `function` parameter
        - set_signature()                — validates the `function` parameter
        - signature_from()               — validates the `function` parameter
        - apply_signature_to_wraps()     — validates the `function` parameter

    Raises:
        SignatureParameterError(TypeError): If the value is not callable.
    """
    if not callable(value):
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = value_name,
            value       = value,
            expected    = "a callable object (function, method, lambda, or class with __call__)",
            problem     = f"'{value_name}' must be callable, but got {type(value).__name__!r}.",
            how_to_fix  = (
                f"Pass a function or callable object as '{value_name}'.",
                "Example: def my_func(): ... → pass my_func (without parentheses).",
                "Lambdas are also valid: lambda x: x",
            ),
            get_location = 2,
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_callable

## Purpose
Validates that the provided value is callable — a function, method, lambda,
or any object with `__call__`. Used wherever the library expects a callable
as input.

## When it is called
- `SignatureCreator.__init__()`   — `base_func_first` parameter
- `get_signature()`               — `function` parameter
- `set_signature()`               — `function` parameter
- `signature_from()`              — `function` parameter
- `apply_signature_to_wraps()`    — `function` parameter

## Notes
- Uses `callable()` — the broadest possible check, accepts anything with `__call__`.
- `get_location=2` points the error to the caller's call site.
"""