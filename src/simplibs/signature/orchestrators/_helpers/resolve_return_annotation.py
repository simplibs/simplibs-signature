import inspect
from inspect import isclass
from typing import Any
from simplibs.sentinels import UNSET
from simplibs.validate import validate_call
# Outers
from ...tools.operations import get_signature


@validate_call
def resolve_return_annotation(
    return_source: Any,
    *,
    _validate_call: bool = True
) -> Any:
    """Turn a return source into the final return annotation.

    Args:
        return_source: `UNSET` for no annotation, a plain callable whose return
            annotation is taken, or an annotation itself (a type, `None`, a string,
            a union, a generic).
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        The annotation, or `inspect.Signature.empty` for none.

    Raises:
        ParamError: If the callable's signature cannot be read.
    """

    # 1. No source given
    if return_source is UNSET:
        return inspect.Signature.empty

    # 2. A plain callable (not a class, not a typing construct): take its return annotation
    if (
        callable(return_source)
        and not isclass(return_source)
        and not hasattr(return_source, "__origin__")
    ):
        return get_signature(
            function=return_source,
            _validate_call=False
        ).return_annotation

    # 3. A direct annotation (type, None, string, Union...)
    return return_source


_DESIGN_NOTES = """
# resolve_return_annotation — A Type or a Function to Copy It From

## Purpose
`create_signature(return_source=...)` accepts the annotation itself and, for
convenience, a function to take it from: `return_source=other_function`.

## How a Callable Is Told From an Annotation
A class is callable too, and so are `list[int]` and other generics, yet they
are annotations. A source counts as "a function to copy from" only if it is
callable, not a class and has no `__origin__`. Everything else, `None`
included, is used as the annotation.

## `UNSET`, Not `None`
`None` is a valid annotation (returns nothing), so "not given" needs a marker
of its own. It becomes `inspect.Signature.empty`.
"""
