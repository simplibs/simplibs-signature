import inspect
from typing import Callable, Any, Iterable
from simplibs.sentinels import UNSET
from simplibs.validate import validate_call
# Outers
from ..collector import ParameterCollector
from ..tools.operations import get_signature, compose_signature


@validate_call(materialize_iterators=True)
def copy_signature(
    function: Callable,
    *,
    return_annotation: Any = UNSET,
    extra_params: Iterable[inspect.Parameter] = (),
    excluded_names: Iterable[str] = (),
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
) -> inspect.Signature:
    """Create a changed copy of a callable's signature.

    Parameters can be removed, added or replaced, and the return annotation
    changed, in one operation. The original is not touched.

    Args:
        function: The callable to copy the signature from.
        return_annotation: The new return annotation. `UNSET` keeps the original.
        extra_params: Parameters to add after the copied ones.
        excluded_names: Names of parameters to leave out.
        accept_double: If False, a name collision raises `ParamError`. If True,
            `replace_double` decides who wins.
        replace_double: True: the later parameter replaces the earlier one.
            False: the earlier one stays. In flat mode the later one is kept as
            well, renamed to `name_1`, `name_2`, ...
        include_variadic: If False, every `*args` and `**kwargs` is left out,
            whatever it is called.
        include_binding: If False, parameters named `self` and `cls` are left out.
        flat_to_kwargs: If True, every parameter becomes keyword-only; `*args`
            is dropped and all `**kwargs` merge into one.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        A new `inspect.Signature`.

    Raises:
        ParamError: If the signature cannot be read, a name collision is refused
            or the order of the result is invalid.
    """

    # 1. Get base signature from the function
    signature = get_signature(
        function=function,
        _validate_call=False
    )

    # 2. Initialize parameter collector with configuration
    param_collector = ParameterCollector(
        excluded_names=excluded_names,
        include_variadic=include_variadic,
        include_binding=include_binding,
        accept_double=accept_double,
        replace_double=replace_double,
        flat_to_kwargs=flat_to_kwargs,
        _validate_call=False
    )

    # 3. Load original signature parameters into the collector
    param_collector.add_params(
        params=signature.parameters.values(),
        _validate_call=False
    )

    # 4. Add extra parameters to the collector
    param_collector.add_params(
        params=extra_params,
        _validate_call=False
    )

    # 5. Determine final return annotation
    final_return = (
        return_annotation
        if return_annotation is not UNSET
        else signature.return_annotation
    )

    # 6. Compose the final signature
    return compose_signature(
        parameters=param_collector.get_ordered_params(),
        return_annotation=final_return,
        _validate_call=False
    )


_DESIGN_NOTES = """
# copy_signature — One Callable's Signature, Modified

## Purpose
The common case of `create_signature`: start from one function, then adjust.
The original parameters are loaded first and `extra_params` second, so with
`replace_double=True` the extras win.

## `return_annotation` Is the Annotation Itself
Unlike `create_signature(return_source=...)` it takes no callable to copy from:
the source function is already the one being copied. `UNSET` keeps its own
annotation, so `None` can still be requested.

## Trusting Its Own Callers
Every inner call passes `_validate_call=False`. The arguments were checked by
this function's own `@validate_call`, so checking them again at every level
would only repeat the work.

## Used by
`signature_copy` and by anyone who wants the signature as an object.
"""
