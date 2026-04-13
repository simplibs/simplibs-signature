from typing import Any
# Outers
from ..exceptions import SignatureParameterError


def validate_is_callable(
    value: Any,
    value_name: str = "function"
) -> None:
    """
    Validates that the provided value is callable (a function or callable object).

    Args:
        value: The value to verify.
        value_name: The name of the parameter for error messages.

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
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_callable

## Purpose
Validates that the provided value is callable — a function, method, lambda,
or any object with `__call__`. Used wherever the library expects a callable
as input for signature extraction or application.

## Where it is used
- `get_signature()` — validates the callable before introspection.
- `set_signature()` — validates the callable before signature assignment.
- `apply_signature_to_wraps()` — validates the wrapped function in decorator context.
- `@signature` decorator — validates the decorated function at decoration time.
- `@signature_copy` decorator — validates the decorated function at decoration time.

## Validation Method
Uses `callable()` — the broadest possible check, accepts anything with `__call__`
including functions, methods, lambdas, and classes with `__call__` defined.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
- Intentionally permissive — doesn't check introspectability, only callability.
- Actual signature extraction happens later in the pipeline where more detailed
  errors can be raised if the callable is not introspectable.
"""