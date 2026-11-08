from typing import Callable, NoReturn
from simplibs.exception import ParamError


def raise_signature_introspection_type_error(
    function: Callable,
    caught_exception: TypeError
) -> NoReturn:
    """Raise the error for an object that `inspect.signature` does not support.

    Args:
        function: The object that was being introspected.
        caught_exception: The `TypeError` raised by `inspect.signature`.

    Raises:
        ParamError: Always, with `caught_exception` as the intercepted exception.
    """

    raise ParamError(
        error_name="SIGNATURE INTROSPECTION ERROR",
        label="function",
        value=function,
        expected="a callable supported by inspect.signature()",
        problem="The object type is not supported by inspect.signature().",
        how_to_fix=(
            "Pass a regular function, method, lambda, or class with __call__.",
            "Ensure the object is not a raw C extension or unsupported callable type.",
        ),
        context="inspect.signature() — unsupported callable type",
        exception=caught_exception,
    )


_DESIGN_NOTES = """
# raise_signature_introspection_type_error — Not Something to Introspect

## Purpose
`inspect.signature` answers with a `TypeError` for objects it cannot
treat as callables. Raised by `get_signature`.

## Intercepting the `TypeError`
`exception=caught_exception` keeps the original error in the MRO.
"""
