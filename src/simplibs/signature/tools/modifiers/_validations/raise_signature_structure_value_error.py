from typing import Iterable, NoReturn
import inspect
from simplibs.exception import ParamError


def raise_signature_structure_value_error(
    params_to_add: Iterable[inspect.Parameter],
    caught_exception: ValueError
) -> NoReturn:
    """Raise the error for a result that `inspect` refuses as a signature.

    Args:
        params_to_add: The parameters that were being added.
        caught_exception: The `ValueError` raised by `Signature.replace`.

    Raises:
        ParamError: Always, with `caught_exception` as the intercepted exception.
    """

    raise ParamError(
        error_name = "SIGNATURE STRUCTURE ERROR",
        label = "params_to_add",
        value = params_to_add,
        expected = "parameters that form a valid Python signature",
        problem = "The resulting signature structure is invalid (e.g. invalid order or duplicate names).",
        how_to_fix = (
            "Check if the combination of existing and new parameters violates Python rules.",
            "Verify parameter order follows: POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, *args, KEYWORD_ONLY, **kwargs.",
            "Verify that no parameter name occurs twice.",
        ),
        context = "inspect.Signature.replace() — structural validation",
        exception = caught_exception,
    )


_DESIGN_NOTES = """
# raise_signature_structure_value_error — The Result Is Not a Signature

## Purpose
The answer to a `ValueError` from `Signature.replace` in
`add_params_to_signature`. The collector keeps order and names valid, so this
is a safety net rather than an everyday message.

## Intercepting the `ValueError`
`exception=caught_exception` keeps the original error in the MRO, so
`except ValueError` still catches it.
"""
