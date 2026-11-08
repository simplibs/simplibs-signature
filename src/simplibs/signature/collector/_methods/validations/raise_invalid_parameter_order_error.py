from typing import NoReturn
import inspect
from simplibs.exception import ParamError


def raise_invalid_parameter_order_error(
    param: inspect.Parameter
) -> NoReturn:
    """Raise the error for a required positional parameter after an optional one.

    Args:
        param: The required parameter that was being added.

    Raises:
        ParamError: Always (also catchable as `SyntaxError`).
    """

    raise ParamError(
        error_name = "INVALID PARAMETER ORDER",
        label = "param.name",
        value = param.name,
        expected = "non-default parameters before default parameters",
        problem = (
            f"Parameter '{param.name}' (no default value) cannot follow "
            "parameters that already have default values."
        ),
        how_to_fix = (
            "Ensure all mandatory parameters (without defaults) are added "
            "before optional parameters (with defaults).",
            "Check the order of your sources or extra_params.",
        ),
        exception = SyntaxError,
    )


_DESIGN_NOTES = """
# raise_invalid_parameter_order_error — Required After Optional

## Purpose
Raised by `_positional_empty_order_check`: Python does not allow
`def f(a=1, b)`.

## Also a `SyntaxError`
`exception=SyntaxError` puts it into the MRO. It is the error Python itself
raises for this shape, so callers who already catch it keep working.

## Label
`param.name`, the same label as the duplicate error, so the two read alike.
"""
