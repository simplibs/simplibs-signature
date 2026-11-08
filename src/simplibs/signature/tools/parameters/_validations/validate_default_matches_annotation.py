from typing import Any
import inspect
from simplibs.exception import ParamError


def validate_default_matches_annotation(
    default_value: Any,
    annotation: Any,
) -> None:
    """Check a default value against its annotation, in the clear cases only.

    The check runs only when the answer is certain: the default is given and
    is not `None`, and the annotation is a plain class. `Any`, unions,
    `Optional` and other typing constructs are not judged.

    Args:
        default_value: The default to check.
        annotation: The annotation to check it against.

    Raises:
        ParamError: If the default is not an instance of the annotated class
            (also catchable as `TypeError`).
    """

    # 1. Skip validation if nothing to check or annotation not suitable
    if (
        default_value is inspect.Parameter.empty
        or default_value is None
        or annotation is inspect.Parameter.empty
        or annotation is Any
    ):
        return  # Nothing deterministic to validate

    if isinstance(annotation, type):
        if not isinstance(default_value, annotation):
            raise ParamError(
                error_name = "INVALID DEFAULT VALUE",
                label = "default for parameter",
                value = default_value,
                expected = f"value of type {annotation.__name__}",
                problem = f"The default value does not match its annotation {annotation.__name__!r}.",
                how_to_fix = (
                    f"Provide a default value of type {annotation.__name__}.",
                    "If unsure, remove the default or adjust the annotation.",
                ),
                exception = TypeError,
            )


_DESIGN_NOTES = """
# validate_default_matches_annotation — A Light Sanity Check

## Purpose
`create_keyword_parameter(name, annotation=int, default="x")` is almost
certainly a typo, and it is cheap to catch while the parameter is being built.

## Deliberately Light
Only a plain class annotation and a real default are judged. Judging
`list[int]`, `int | None` or a `Protocol` means reimplementing a type checker,
and a wrong "no" would block a valid signature. `None` is skipped because it is
the usual default of an optional parameter whatever its annotation says.

## Also a `TypeError`
`exception=TypeError` puts it into the MRO, so `except TypeError` still works.
"""
