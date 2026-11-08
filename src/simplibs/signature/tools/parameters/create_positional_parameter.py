import inspect
from typing import Any
from simplibs.validate import validate_call
# Inners
from ._validations import validate_default_matches_annotation


@validate_call
def create_positional_parameter(
    name: str,
    *,
    annotation: Any = inspect.Parameter.empty,
    default: Any = inspect.Parameter.empty,
    positional_only: bool = False,
    _validate_call: bool = True
) -> inspect.Parameter:
    """Create a positional parameter.

    By default the parameter is ordinary (passed by position or by name);
    with `positional_only=True` it can only be passed by position.

    Args:
        name: The parameter name.
        annotation: The annotation. Default: no annotation.
        default: The default value. Default: no default (required).
        positional_only: If True, the parameter is positional-only.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments and the check of `default` against
            `annotation`.

    Returns:
        An `inspect.Parameter` of kind `POSITIONAL_ONLY` or `POSITIONAL_OR_KEYWORD`.

    Raises:
        ParamError: If `default` does not fit a plain class `annotation`.
    """

    # 1. A default that contradicts its annotation is refused (unless validation is off)
    if _validate_call:
        validate_default_matches_annotation(default, annotation)

    # 2. Resolve the parameter kind
    kind = (
        inspect.Parameter.POSITIONAL_ONLY
        if positional_only
        else inspect.Parameter.POSITIONAL_OR_KEYWORD
    )

    # 3. Build the parameter
    return inspect.Parameter(
        name = name,
        kind = kind,
        default = default,
        annotation = annotation,
    )


_DESIGN_NOTES = """
# create_positional_parameter — A Positional Parameter in One Call

## Purpose
Spares the caller `inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD, ...)`.
One function covers both positional kinds, because the only difference is a
flag.

## `positional_only`
A flag instead of a second function: the two kinds share everything else, and
`positional_only=False` is the common case.

## Two Uses of `_validate_call`
It bypasses `@validate_call`'s own checks, and it also gates the default/annotation
check in the body, so one switch turns off every check of this function.
"""
