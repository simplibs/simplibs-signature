from typing import Callable, NoReturn
from simplibs.exception import ParamError


def raise_signature_introspection_value_error(
    function: Callable,
    caught_exception: ValueError
) -> NoReturn:
    """Raise the error for a callable whose signature cannot be read.

    Args:
        function: The object that was being introspected.
        caught_exception: The `ValueError` raised by `inspect.signature`.

    Raises:
        ParamError: Always, with `caught_exception` as the intercepted exception.
    """

    raise ParamError(
        error_name="SIGNATURE INTROSPECTION ERROR",
        label="function",
        value=function,
        expected="a function with an introspectable signature",
        problem="The function's signature cannot be introspected (e.g. built-in without signature metadata).",
        how_to_fix=(
            "Use a pure Python function or a callable with a defined signature.",
            "Built-in functions like len() or print() may not expose their signature.",
            "If wrapping a built-in, define a wrapper function with an explicit signature.",
        ),
        context="inspect.signature() — signature introspection failed",
        exception=caught_exception,
    )


_DESIGN_NOTES = """
# raise_signature_introspection_value_error — No Signature to Read

## Purpose
Built-ins implemented in C often carry no signature metadata, and
`inspect.signature` answers with a `ValueError`. Raised by `get_signature`.

## Intercepting the `ValueError`
`exception=caught_exception` keeps the original error in the MRO.
"""
