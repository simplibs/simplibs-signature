import inspect
from typing import Callable
# Commons
from .._validations import validate_is_callable, validate_is_inspect_signature


def set_signature(
    function: Callable,
    signature: inspect.Signature,
    validate: bool = True
) -> Callable:
    """
    Assigns an inspect.Signature directly to a function via __signature__.

    Args:
        function:  The function to which the signature will be assigned.
        signature: The signature to assign.
        validate:  If True, validates the input arguments (default: True).

    Returns:
        The original function with the assigned signature.

    Raises:
        SignatureParameterError(TypeError): If `function` is not callable.
        SignatureParameterError(TypeError): If `signature` is not an inspect.Signature.
    """
    if validate:
        validate_is_callable(function, "function")
        validate_is_inspect_signature(signature, "signature")

    function.__signature__ = signature
    return function


_DESIGN_NOTES = """
# set_signature

## Purpose
Assigns an `inspect.Signature` directly to a function by setting its
`__signature__` attribute. The counterpart to `get_signature()` — together
they form the read/write interface for signature manipulation in the library.

## Why validate=False exists
Internal library calls already know their inputs are valid — re-validating
on every internal call would be redundant. `validate=False` skips both input
checks and is used exclusively for internal calls. External callers should
always use the default `validate=True`.

## Notes
- Returns the original function — allows chaining or inline assignment.
- Setting `__signature__` is the standard Python mechanism for overriding
  what `inspect.signature()` reports for a callable.
- `get_location` is not set — this function does not raise on its own,
  it delegates all raising to the two validation functions.
"""