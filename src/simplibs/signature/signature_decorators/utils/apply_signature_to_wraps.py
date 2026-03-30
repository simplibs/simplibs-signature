import inspect
from typing import Callable
from functools import wraps
# Commons
from ...utils import validate_is_callable, validate_is_inspect_signature


def apply_signature_to_wraps(
    function: Callable,
    signature: inspect.Signature,
    validate: bool = True
) -> Callable:
    """
    Creates a wrapper around a function with an assigned inspect.Signature.

    Unlike set_signature(), this creates a new callable around the original
    function — use this utility when building decorators that need to wrap
    a function and assign a custom signature at the same time.

    Args:
        function:  The function to be wrapped.
        signature: The signature to assign to the wrapper.
        validate:  If True, validates the input arguments (default: True).

    Returns:
        A new wrapper with the assigned signature, preserving the original
        function's metadata.

    Raises:
        SignatureParameterError(TypeError): If `function` is not callable.
        SignatureParameterError(TypeError): If `signature` is not an inspect.Signature.
    """

    # 1. Validate inputs
    if validate:
        validate_is_callable(function, "function")
        validate_is_inspect_signature(signature, "signature")

    # 2. Define the wrapper
    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)

    # 3. Assign the signature
    wrapper.__signature__ = signature

    # 4. Return the wrapper
    return wrapper


_DESIGN_NOTES = """
# apply_signature_to_wraps

## Purpose
Creates a new callable wrapper around a function and assigns a custom
`inspect.Signature` to it. The primary building block for signature-aware
decorators in this library.

## set_signature() vs apply_signature_to_wraps()
Both assign a signature — but they serve different purposes:

- `set_signature()` assigns the signature directly to the original function.
  No wrapper is created. Use when the function itself should report a
  different signature.
- `apply_signature_to_wraps()` creates a new wrapper via `@wraps` and assigns
  the signature to the wrapper. Use when building a decorator that needs to
  wrap the function in a new callable with a controlled signature.

## Why @wraps is used
`@wraps(function)` copies metadata from the original function to the wrapper
(`__name__`, `__doc__`, `__module__`, etc.) — so the wrapper is transparent
to introspection tools. The `__signature__` is then overridden explicitly,
which takes precedence over whatever `@wraps` would have copied.

## Notes
- The validation order was corrected from the original — `validate_is_callable`
  now runs before `validate_is_inspect_signature`, consistent with the
  parameter order in the function signature.
- `get_location` is not set — this function does not raise on its own,
  it delegates all raising to the two validation functions.
"""