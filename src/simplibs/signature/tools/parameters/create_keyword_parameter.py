import inspect
from typing import Any
from simplibs.validate import validate_call
# Inners
from ._validations import validate_default_matches_annotation


@validate_call
def create_keyword_parameter(
    name: str,
    *,
    annotation: Any = inspect.Parameter.empty,
    default: Any = inspect.Parameter.empty,
    _validate_call: bool = True
) -> inspect.Parameter:
    """Create a keyword-only parameter.

    A keyword-only parameter can only be passed by name; it stands after
    `*args` (or a bare `*`) in a signature.

    Args:
        name: The parameter name.
        annotation: The annotation. Default: no annotation.
        default: The default value. Default: no default (required).
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments and the check of `default` against
            `annotation`.

    Returns:
        An `inspect.Parameter` of kind `KEYWORD_ONLY`.

    Raises:
        ParamError: If `default` does not fit a plain class `annotation`.
    """

    # 1. A default that contradicts its annotation is refused (unless validation is off)
    if _validate_call:
        validate_default_matches_annotation(default, annotation)

    # 2. Build the parameter
    return inspect.Parameter(
        name = name,
        kind = inspect.Parameter.KEYWORD_ONLY,
        default = default,
        annotation = annotation,
    )


_DESIGN_NOTES = """
# create_keyword_parameter — A Keyword-Only Parameter in One Call

## Purpose
`inspect.Parameter("x", inspect.Parameter.KEYWORD_ONLY, default=1)` hides the
interesting part (the name and the default) behind the kind. This function says
only what a caller means.

## Keyword-Only Arguments
`annotation` and `default` must be named, so a call never has to be decoded by
position.

## Two Uses of `_validate_call`
It bypasses `@validate_call`'s own checks, and it also gates the default/annotation
check in the body, so one switch turns off every check of this function.
"""
