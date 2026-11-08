from typing import Iterable, NoReturn
import inspect
from simplibs.exception import ParamError


def raise_signature_composition_type_error(
    parameters: Iterable[inspect.Parameter],
    caught_exception: TypeError
) -> NoReturn:
    """Raise the error for parameters or annotations of an unusable type.

    Args:
        parameters: The parameters that were being composed.
        caught_exception: The `TypeError` raised while composing.

    Raises:
        ParamError: Always, with `caught_exception` as the intercepted exception.
    """

    raise ParamError(
        error_name = "SIGNATURE COMPOSITION ERROR",
        label = "parameters",
        value = parameters,
        expected = "an iterable of inspect.Parameter instances",
        problem = "The parameters collection or return_annotation is of an unsupported type.",
        how_to_fix = (
            "Ensure all items in the parameters collection are inspect.Parameter instances.",
            "Use create_keyword_parameter() and create_positional_parameter() to construct parameters.",
        ),
        context = "inspect.Signature() — type mismatch during construction",
        exception = caught_exception,
    )


_DESIGN_NOTES = """
# raise_signature_composition_type_error — Wrong Kind of Input

## Purpose
Covers a collection that is not iterable and items or annotations of an
unsupported type. Raised by `compose_signature`.

## Intercepting the `TypeError`
`exception=caught_exception` keeps the original error in the MRO.
"""
