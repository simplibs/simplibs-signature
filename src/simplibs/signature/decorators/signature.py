import inspect
from typing import Callable, Any, Iterable
from simplibs.sentinels import UNSET
from simplibs.validate import validate_call
# Outers
from ..orchestrators import create_signature
# Inners
from .builders import apply_signature_to_wraps


@validate_call(materialize_iterators=True)
def signature(
    *params: inspect.Parameter | Callable,
    returns: Any = UNSET,
    excepts: Iterable[str] = (),
    use_func: bool = True,
    func_first: bool = True,
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
) -> Callable:
    """Decorator factory that builds the signature of a function from several sources.

    The decorated function's own signature can be part of the result, merged
    with extra parameters and callables, filtered and reordered.

    Args:
        *params: Extra `inspect.Parameter` objects or callables to merge in.
        returns: `UNSET` for no annotation, a callable gives its return
            annotation, anything else is used as the annotation.
        excepts: Names of parameters to leave out.
        use_func: If True, the decorated function's own parameters are part
            of the result.
        func_first: If True, the function's parameters come before `*params`,
            so `*params` win collisions. If False, the other way round.
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
        A decorator that returns a wrapper reporting the assembled signature.

    Raises:
        ParamError: When the decorator is created or applied, if a source is
            invalid, a collision is refused or the order is invalid.
    """

    # 1. Define the decorator
    def decorator(function: Callable) -> Callable:

        # 2. The function is one of the sources: before `params` or behind them
        param_sources = params
        if use_func:
            param_sources = (
                (function,) + param_sources if func_first
                else param_sources + (function,)
            )

        # 3. Assemble the signature from all sources
        new_signature = create_signature(
            *param_sources,
            return_source = returns,
            excluded_names = tuple(excepts),
            accept_double = accept_double,
            replace_double = replace_double,
            include_variadic = include_variadic,
            include_binding = include_binding,
            flat_to_kwargs = flat_to_kwargs,
            _validate_call = False
        )

        # 4. Wrap the function and apply the assembled signature
        return apply_signature_to_wraps(
            function = function,
            signature = new_signature,
            _validate_call = False
        )

    # 5. Return the decorator
    return decorator


_DESIGN_NOTES = """
# signature — Describe a Function's Signature From Several Sources

## Purpose
A wrapper usually looks like `(*args, **kwargs)`, and tools then see nothing.
`@signature(...)` assembles what the wrapper really accepts from the function
it wraps and from whatever else is listed.

## Where the Function Goes
With `use_func=True` the decorated function is added to the sources, in front
(`func_first=True`) or behind. Position is priority: with `replace_double=True`
the later source wins a collision.

## Why the Signature Is Built When the Decorator Is Applied
The decorated function is only known then, so `create_signature` runs inside
the inner `decorator`, not in the factory.

## Trusting Its Own Calls
The factory's arguments are checked by its own `@validate_call`. The inner calls
pass `_validate_call=False`.

## Related
`signature_copy` starts from one callable, `signature_set` attaches a finished
signature.
"""
