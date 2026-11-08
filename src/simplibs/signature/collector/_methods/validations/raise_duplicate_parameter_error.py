import inspect
from typing import NoReturn
from simplibs.exception import ParamError


def raise_duplicate_parameter_error(
    param: inspect.Parameter,
    existing_name: str | None = None,
) -> NoReturn:
    """Raise the error for a parameter that collides with one already stored.

    Args:
        param: The parameter that was being added.
        existing_name: The name of the stored parameter it collides with.
            `None`, or the same name, for an ordinary name collision. A
            different name means a second `*args` or `**kwargs`.

    Raises:
        ParamError: Always (also catchable as `ValueError`).
    """

    # 1. Same name, or a second variadic of a kind that is already stored
    if existing_name is None or existing_name == param.name:
        problem = f"Parameter '{param.name}' is already defined in this signature."
    else:
        problem = (
            f"Parameter '{param.name}' collides with the already defined "
            f"{param.kind.description} parameter '{existing_name}'; "
            "a signature can have only one of each."
        )

    # 2. Raise
    raise ParamError(
        error_name = "DUPLICATE PARAMETER ERROR",
        label = "param.name",
        value = param.name,
        expected  = "a unique parameter name",
        problem = problem,
        how_to_fix = (
            f"Ensure that the parameter name '{param.name}' is unique within the signature.",
            "If you intend to overwrite existing parameters, set 'accept_double=True' in the collector.",
            "Check if you are accidentally adding the same source or function multiple times.",
        ),
        exception = ValueError,
    )


_DESIGN_NOTES = """
# raise_duplicate_parameter_error — A Name Is Taken

## Purpose
The one place the message for a collision is written. Raised by `add_param` and
by flat mode when `accept_double=False`.

## Two Kinds of Collision
The same name twice is the obvious one. A second `*args` (or `**kwargs`) under
another name is the other: `inspect` accepts `(*a, *b)` without complaint, so
the collector refuses it first. `existing_name` tells the two apart and the
message names the stored parameter.

## Also a `ValueError`
`exception=ValueError` puts it into the MRO, so `except ValueError` still works.
"""
