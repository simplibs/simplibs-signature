from typing import Iterable, NoReturn
import inspect
from simplibs.exception import ParamError


def raise_signature_composition_value_error(
    parameters: Iterable[inspect.Parameter],
    caught_exception: ValueError
) -> NoReturn:
    """Raise the error for parameters that do not form a valid signature.

    Args:
        parameters: The parameters that were being composed.
        caught_exception: The `ValueError` raised by `inspect.Signature`.

    Raises:
        ParamError: Always, with `caught_exception` as the intercepted exception.
    """

    raise ParamError(
        error_name = "SIGNATURE COMPOSITION ERROR",
        label = "parameters",
        value = parameters,
        expected = "a collection of valid, uniquely named inspect.Parameter instances",
        problem = "One or more parameters are structurally invalid (e.g. duplicates or wrong order).",
        how_to_fix = (
            "Ensure all parameter names are unique.",
            "Check that order follows: POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, *args, KEYWORD_ONLY, **kwargs.",
            "Verify that each parameter is a valid inspect.Parameter instance.",
        ),
        context = "inspect.Signature() — invalid parameter structure",
        exception = caught_exception,
    )


_DESIGN_NOTES = """
# raise_signature_composition_value_error — Not a Valid Signature

## Purpose
The answer to a `ValueError` from `inspect.Signature(...)`: a wrong order
of kinds, a duplicate name, a required parameter after an optional one.
Raised by `compose_signature`.

## Intercepting the `ValueError`
`exception=caught_exception` keeps the original error in the MRO, so
`except ValueError` still catches it.
"""
