# Commons
from ...utils import SignatureParameterError


def validate_is_type_or_callable(value, value_name: str) -> None:
    """
    Validates that the provided value is a type or a callable object.

    Usage:
        - SignatureCreator.__init__() — validates the `return_type` parameter

    The `return_type` parameter in SignatureCreator accepts:
        - type      → used directly as the return annotation (e.g. int, str, MyClass)
        - callable  → return annotation is extracted from its signature
        - None      → no return annotation (validation is skipped)
        - UNSET     → return type is inherited from base_func (validation is skipped)

    Raises:
        SignatureParameterError(TypeError): If the value is neither a type nor callable.
    """
    if not isinstance(value, type) and not callable(value):
        raise SignatureParameterError(
            error_name  = "INVALID ARGUMENT ERROR",
            value_label = value_name,
            value       = value,
            expected    = "a type (e.g. int, str, MyClass) or a callable (function whose return annotation will be used)",
            problem     = f"'{value_name}' must be a type or callable, but got {type(value).__name__!r}.",
            how_to_fix  = (
                "Pass a type directly: return_type=int.",
                "Pass a callable to extract its return annotation: return_type=my_func.",
                "To explicitly disable return annotation: return_type=None.",
                "To inherit return type from base_func: omit return_type (uses UNSET by default).",
            ),
            get_location = 2,
            context      = "SignatureCreator.__init__() — return_type type check",
            exception    = TypeError,
        )


_DESIGN_NOTES = """
# validate_is_type_or_callable

## Purpose
Validates that the provided value is either a type (class) or a callable.
Used exclusively in `SignatureCreator.__init__()` to guard the `return_type`
parameter — which has four valid states, two of which bypass this validation
entirely.

## When it is called
- `SignatureCreator.__init__()` — `return_type` parameter
- Only when `return_type` is not `None` and not `UNSET` — those two states
  are handled upstream before this function is called.

## Notes
- Uses `isinstance(value, type)` for types and `callable()` for callables —
  not `isinstance(value, typing.Callable)`, which is an implementation detail
  and behaves inconsistently across Python versions.
- `context` is kept — it identifies the exact parameter and class, which is
  not obvious from the function name alone.
- `get_location=2` points the error to the caller's call site.
"""