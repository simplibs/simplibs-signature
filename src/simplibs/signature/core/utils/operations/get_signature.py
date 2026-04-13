import inspect
from typing import Callable
# Outers
from ...validators import SignatureBuildError, validate_is_callable


def get_signature(
    function: Callable,
    *,
    validate: bool = True
) -> inspect.Signature:
    """
    Safely retrieves an inspect.Signature from the provided callable.

    Args:
        function: A function or callable object whose signature is to be retrieved.
        validate: If True, validates the input argument.

    Returns:
        inspect.Signature of the provided function.

    Raises:
        SignatureParameterError(TypeError): If `function` is not callable.
        SignatureBuildError(ValueError):    If the function's signature cannot be introspected.
        SignatureBuildError(TypeError):     If the object type is not supported by inspect.signature().
    """

    # 1. Validations
    if validate:
        validate_is_callable(function)

    # 2. Signature introspection
    try:
        return inspect.signature(function)

    except ValueError as e:
        raise SignatureBuildError(
            error_name  = "SIGNATURE INTROSPECTION ERROR",
            value_label = "function",
            value       = function,
            expected    = "a function with an introspectable signature",
            problem     = "The function's signature cannot be introspected (e.g. built-in without signature metadata).",
            how_to_fix  = (
                "Use a pure Python function or a callable with a defined signature.",
                "Built-in functions like len() or print() may not expose their signature.",
                "If wrapping a built-in, define a wrapper function with an explicit signature.",
            ),
            context     = "inspect.signature() — signature introspection failed",
            exception   = e,
        ) from e

    except TypeError as e:
        raise SignatureBuildError(
            error_name  = "SIGNATURE INTROSPECTION ERROR",
            value_label = "function",
            value       = function,
            expected    = "a callable supported by inspect.signature()",
            problem     = "The object type is not supported by inspect.signature().",
            how_to_fix  = (
                "Pass a regular function, method, lambda, or class with __call__.",
                "Ensure the object is not a raw C extension or unsupported callable type.",
            ),
            context      = "inspect.signature() — unsupported callable type",
            exception    = e,
        ) from e


_DESIGN_NOTES = """
# get_signature

## Purpose
A safe wrapper around `inspect.signature()`. Serves as the single point of
contact for signature introspection, converting standard Python exceptions
into structured `SignatureBuildError` instances with diagnostic information.

## Where it is used
- User-facing utility for extracting signatures from existing functions.
- Used internally by `SignatureCreator` when processing callable parameter sources.
- Foundation for signature-based inspection and manipulation workflows.

## Validation Hierarchy (Multi-Layered Defense)
When `validate=True`:
1. `validate_is_callable()` — catches common user errors (None, strings, integers)
   and raises `SignatureParameterError` with helpful guidance.
2. `try-except TypeError` — fallback for exotic objects that pass `callable()`
   but are unsupported by `inspect` (e.g., certain C-extension objects).
3. `try-except ValueError` — handles valid Python callables lacking introspection
   metadata (e.g., some built-ins like `len()` or `print()`).

## Why validate=False Exists
Internal library calls often pass objects already validated elsewhere. Using
`validate=False` avoids redundant checks, improving performance without
sacrificing safety through careful internal code practices.

## Failure Semantics
- `ValueError` → "I recognize this as callable, but I cannot see its signature."
- `TypeError` → "I don't know how to introspect this object's signature."

## Exception Chaining
Both `except` blocks use `from e` to preserve the original exception context,
aiding debugging while providing structured error output to users.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Location tracking is inherited from `SignatureError` — no manual offset needed.
- All validation errors will consistently point to the user's calling code.
- `context` field preserves which introspection step failed for clarity.
- This function is read-only — see `set_signature()` for write operations.
"""