import inspect
from typing import Callable
from simplibs.validate import validate_call


@validate_call
def set_signature(
    function: Callable,
    signature: inspect.Signature,
    *,
    _validate_call: bool = True
) -> Callable:
    """Attach a signature to a function through `__signature__`.

    The function itself is changed and returned; no wrapper is made.

    Args:
        function: The function to change.
        signature: The signature to attach.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        The same `function`, now reporting `signature` to `inspect`.
    """

    # 1. Assign signature to function
    function.__signature__ = signature

    # 2. Return the modified function
    return function


_DESIGN_NOTES = """
# set_signature — Changing What `inspect` Reports

## Purpose
`inspect.signature` looks at `__signature__` first, so assigning it changes what
tools, IDEs and documentation generators see, while the code and the real
call behaviour stay as they are.

## No Wrapper
The function is modified in place. Where a separate callable is wanted (for
example one that survives `functools.wraps` of the original), use
`apply_signature_to_wraps`.

## Not Checked Further
The signature is not compared with what the function really accepts. That is the
caller's responsibility; this function only attaches.
"""
