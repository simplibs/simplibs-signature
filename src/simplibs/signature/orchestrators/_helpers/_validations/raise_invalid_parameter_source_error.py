from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_invalid_parameter_source_error(
    index: int,
    item: Any
) -> NoReturn:
    """Raise the error for a source that is neither a parameter nor a callable.

    Args:
        index: The position of the source among the given sources.
        item: The source itself.

    Raises:
        ParamError: Always (also catchable as `TypeError`).
    """

    raise ParamError(
        error_name = "INVALID PARAMETER SOURCE",
        label = f"param_sources[{index}]",
        value = item,
        expected = "an inspect.Parameter or a callable (function/method)",
        problem = (
            f"Item at index {index} is of type {type(item).__name__!r}, "
            "which is not a valid source for parameters."
        ),
        how_to_fix = (
            "Ensure all positional arguments are either Parameter instances or callables.",
            "If you are passing a list of sources, remember to unpack it: create_signature(*my_list).",
            "Use create_keyword_parameter() or create_positional_parameter() to build parameters.",
        ),
        exception = TypeError,
    )


_DESIGN_NOTES = """
# raise_invalid_parameter_source_error — Not a Source

## Purpose
`create_signature(*sources)` takes parameters and callables. Anything else (a
string, a list that was not unpacked) is named here by its position and type.
Raised by `load_param_sources`, which is the only place that needs it.

## Also a `TypeError`
`exception=TypeError` puts it into the MRO, so `except TypeError` still works.

## The Unpacking Hint
A list passed whole instead of unpacked is the most common cause, so the message
says `create_signature(*my_list)`.
"""
