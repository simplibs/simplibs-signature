import inspect
from typing import Callable
# Commons
from .._validations import SignatureBuildError, validate_is_callable


def get_signature(
    function: Callable,
    validate: bool = True
) -> inspect.Signature:
    """
    Safely retrieves an inspect.Signature from the provided callable.

    Args:
        function: A function or callable object whose signature is to be retrieved.
        validate: If True, validates the input arguments (default: True).

    Returns:
        inspect.Signature of the provided function.

    Raises:
        SignatureParameterError(TypeError): If `function` is not callable.
        SignatureBuildError(ValueError):    If the function's signature cannot be introspected.
        SignatureBuildError(TypeError):     If the object type is not supported by inspect.signature().
    """
    if validate:
        validate_is_callable(function, "function")

    try:
        return inspect.signature(function)

    except ValueError as e:
        raise SignatureBuildError(
            error_name  = "SIGNATURE ERROR",
            value_label = "function",
            value       = function,
            expected    = "a function with an introspectable signature",
            problem     = "the function's signature cannot be introspected (e.g. built-in without signature metadata).",
            how_to_fix  = (
                "Use a pure Python function or a callable with a defined signature.",
                "Built-in functions like len() or print() may not expose their signature.",
                "If wrapping a built-in, define a wrapper function with an explicit signature.",
            ),
            get_location = 2,
            context     = "inspect.signature() — signature introspection",
            exception   = e,
        )

    except TypeError as e:
        raise SignatureBuildError(
            error_name  = "SIGNATURE ERROR",
            value_label = "function",
            value       = function,
            expected    = "a callable supported by inspect.signature()",
            problem     = "the object type is not supported by inspect.signature().",
            how_to_fix  = (
                "Pass a regular function, method, lambda, or class with __call__.",
                "Make sure the object is not a raw C extension or unsupported callable type.",
            ),
            get_location = 2,
            context      = "inspect.signature() — unsupported callable type",
            exception    = e,
        )


_DESIGN_NOTES = """
# get_signature

## Purpose
A safe wrapper around `inspect.signature()` — retrieves the signature of a
callable and converts any Python-level exceptions into structured
`SignatureBuildError` instances. The single point of contact between the
library and `inspect.signature()`.

## Why validate=False exists
Internal library calls already know their input is valid — re-validating on
every internal call would be redundant. `validate=False` skips the
`validate_is_callable` check and is used exclusively for internal calls.
External callers should always use the default `validate=True`.

## Failure modes
Two distinct failure modes are handled, both raised by `inspect.signature()`:

- `ValueError` — the callable exists and is valid Python, but has no
  introspectable signature metadata (e.g. some built-ins).
- `TypeError`  — the object type is not supported by `inspect.signature()`
  at all (e.g. raw C extensions).

Both are caught and re-raised as `SignatureBuildError` with a structured
message pointing to the call site.

## Notes
- `context` is kept in both raises — it identifies which `inspect.signature()`
  call failed and why, which is not obvious from the error alone.
- `get_location=2` points the error to the caller's call site.
- The import of `SimpleException` has been removed — both failure modes now
  correctly use `SignatureBuildError`.
"""