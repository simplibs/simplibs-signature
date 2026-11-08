import inspect
from typing import Callable, Any, Iterable
from simplibs.sentinels import UNSET
from simplibs.validate import validate_call
# Outers
from ..orchestrators import copy_signature
# Inners
from .builders import create_signature_decorator


@validate_call(materialize_iterators=True)
def signature_copy(
    base_func: Callable,
    *,
    returns: Any = UNSET,
    extras: Iterable[inspect.Parameter] = (),
    excepts: Iterable[str] = (),
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
) -> Callable:
    """Decorator factory that gives a function a changed copy of another's signature.

    A decorator form of `copy_signature`, with shorter parameter names.

    Args:
        base_func: The callable to copy the signature from.
        returns: The new return annotation. `UNSET` keeps the original.
        extras: Parameters to add after the copied ones.
        excepts: Names of parameters to leave out.
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
        A decorator that returns a wrapper reporting the copied signature.

    Raises:
        ParamError: When the decorator is created, if the signature cannot be
            read, a collision is refused or the order is invalid.
    """

    # 1. Create the transformed signature
    signature = copy_signature(
        function = base_func,
        return_annotation = returns,
        extra_params = tuple(extras),
        excluded_names = tuple(excepts),
        accept_double = accept_double,
        replace_double = replace_double,
        include_variadic = include_variadic,
        include_binding = include_binding,
        flat_to_kwargs = flat_to_kwargs,
        _validate_call = False
    )

    # 2. Create and return the decorator
    return create_signature_decorator(
        signature=signature,
        _validate_call=False
    )


_DESIGN_NOTES = """
# signature_copy — "Looks Like That Function, Plus a Little"

## Purpose
The typical wrapper takes the same arguments as the function it wraps, with a
few more or a few less. This decorator copies the signature of that function
and applies it to the wrapper.

## Built When the Decorator Is Created
Unlike `signature`, the source is `base_func`, which is known at once, so the
signature is made in the factory and every decorated function shares it.

## Shorter Names
`returns`, `extras` and `excepts` are the decorator spelling of
`return_annotation`, `extra_params` and `excluded_names`.

## Related
`copy_signature` is the same operation without the decorator.
"""
