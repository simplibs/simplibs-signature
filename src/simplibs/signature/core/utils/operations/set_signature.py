import inspect
from typing import Callable
# Outers
from ...validators import validate_is_callable, validate_is_inspect_signature


def set_signature(
    function: Callable,
    signature: inspect.Signature,
    *,
    validate: bool = True
) -> Callable:
    """
    Assigns an inspect.Signature directly to a function via __signature__.

    Args:
        function:  The function to which the signature will be assigned.
        signature: The signature to assign.
        validate:  If True, validates the input arguments.

    Returns:
        The original function with the assigned signature.

    Raises:
        SignatureParameterError(TypeError): If `function` is not callable.
        SignatureParameterError(TypeError): If `signature` is not an inspect.Signature.
    """

    # 1. Validations
    if validate:
        validate_is_callable(function)
        validate_is_inspect_signature(signature)

    # 2. Assign signature to function
    function.__signature__ = signature

    # 3. Return the modified function
    return function


_DESIGN_NOTES = """
# set_signature

## Purpose
Assigns an `inspect.Signature` directly to a function by setting its
`__signature__` attribute. Serves as the counterpart to `get_signature()` —
together they form the complete read/write interface for signature manipulation.

## Where it is used
- User-facing utility for programmatically assigning signatures to functions.
- Used internally by signature decorators to wrap functions with new signatures.
- Foundation for higher-level signature transformation pipelines.

## How it Works
Setting the `__signature__` attribute is the standard Python mechanism for
overriding what `inspect.signature()` and `inspect.getfullargspec()` report
for a callable. It is widely used in decorator implementations and introspection
libraries.

## Why validate=False Exists
Internal library calls already know their inputs are valid — re-validating on
every internal call would be redundant overhead. `validate=False` is used
exclusively for trusted internal contexts, improving performance.

## Stack Filtering
The `SignatureBuildError` exception automatically skips internal library frames 
via `skip_locations = ("simplibs/signature",)` defined in the base exception class. 
This ensures the error points to user code calling the library, not to internal 
validation helpers. The default `get_location=1` is sufficient because the 
base exception already handles frame filtering.

## Notes
- Returns the original function — allows method chaining or inline assignment.
- The function is modified in-place; the return value is for convenience.
- Works with any callable: functions, methods, lambdas, callable classes.
- Pairs naturally with `get_signature()` for read-modify-write workflows.
"""