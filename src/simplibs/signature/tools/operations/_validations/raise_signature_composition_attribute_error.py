from typing import Iterable, NoReturn
import inspect
from simplibs.exception import ParamError


def raise_signature_composition_attribute_error(
    parameters: Iterable[inspect.Parameter],
    caught_exception: AttributeError
) -> NoReturn:
    """Raise the error for an item that is not a parameter.

    Args:
        parameters: The parameters that were being composed.
        caught_exception: The `AttributeError` raised by `inspect.Signature`.

    Raises:
        ParamError: Always, with `caught_exception` as the intercepted exception.
    """

    raise ParamError(
        error_name = "SIGNATURE COMPOSITION ERROR",
        label = "parameters",
        value = parameters,
        expected = "a collection of inspect.Parameter instances",
        problem = "One or more items in the parameters collection are not valid Parameter objects.",
        how_to_fix = (
            "Ensure all items are created via inspect.Parameter() or our factory functions.",
            "Verify that you are not accidentally passing strings or other objects.",
        ),
        context = "inspect.Signature() — duck typing failed (missing .name)",
        exception = caught_exception,
    )


_DESIGN_NOTES = """
# raise_signature_composition_attribute_error — Something That Is Not a Parameter

## Purpose
`inspect.Signature` reads `.kind` and `.name` of every item. A string or
a number in the collection fails there with an `AttributeError`, which says
nothing about the collection. Raised by `compose_signature`.

## Intercepting the `AttributeError`
`exception=caught_exception` keeps the original error in the MRO.
"""
