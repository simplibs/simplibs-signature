import inspect
from typing import Callable
from simplibs.validate import validate_call
# Inners
from ._validations import (
    raise_signature_introspection_type_error,
    raise_signature_introspection_value_error
)


@validate_call
def get_signature(
    function: Callable,
    *,
    _validate_call: bool = True
) -> inspect.Signature:
    """Get the `inspect.Signature` of a callable.

    Args:
        function: A function, method, class or other callable.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        The signature of `function`.

    Raises:
        ParamError: If the callable has no introspectable signature (also
            catchable as `ValueError`), or is not a supported callable (also
            `TypeError`).
    """

    # 1. Introspect
    try:
        return inspect.signature(function)

    # 2. Handle callables lacking signature metadata
    except ValueError as e:
        raise_signature_introspection_value_error(function, e)

    # 3. Handle objects that cannot be introspected as callables
    except TypeError as e:
        raise_signature_introspection_type_error(function, e)



_DESIGN_NOTES = """
# get_signature — `inspect.signature` With a Readable Failure

## Purpose
`inspect.signature` raises a bare `ValueError` for built-ins such as `len` and a
bare `TypeError` for objects that are not callables. Both messages say little
about which argument was wrong. This wrapper turns them into `ParamError` cards
that name the object and suggest a way out.

## Both Original Types Survive
The errors carry the original type in their MRO, so code that already catches
`ValueError` or `TypeError` keeps working.

## Used by
`copy_signature`, `load_param_sources` and `resolve_return_annotation`, which
call it with `_validate_call=False` because they have checked the argument.
"""
