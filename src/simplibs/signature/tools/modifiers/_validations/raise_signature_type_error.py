from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_signature_type_error(
    ordered_params: Any,
    caught_exception: TypeError
) -> NoReturn:
    """Raise the error for parameters of an unusable type.

    Args:
        ordered_params: The parameters that were being put into the signature.
        caught_exception: The `TypeError` raised by `Signature.replace`.

    Raises:
        ParamError: Always, with `caught_exception` as the intercepted exception.
    """

    raise ParamError(
        error_name = "SIGNATURE TYPE ERROR",
        label = "parameters",
        value = ordered_params,
        expected = "valid inspect.Parameter objects",
        problem = "An unexpected type error occurred during signature reconstruction.",
        how_to_fix = ("Verify that all objects in params_to_add are proper inspect.Parameter instances.",),
        context = "inspect.Signature.replace() — type validation",
        exception=caught_exception,
    )


_DESIGN_NOTES = """
# raise_signature_type_error — Something Is Not a Parameter

## Purpose
The answer to a `TypeError` from `Signature.replace` in
`add_params_to_signature`, for example an item that is not an
`inspect.Parameter`.

## Intercepting the `TypeError`
`exception=caught_exception` keeps the original error in the MRO, so
`except TypeError` still catches it.
"""
