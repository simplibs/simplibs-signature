import inspect
from typing import Callable, Any, Iterable
from simplibs.sentinels import UNSET
from simplibs.validate import validate_call
# Outers
from ..collector import ParameterCollector
from ..tools.operations import compose_signature
# Inners
from ._helpers import load_param_sources, resolve_return_annotation



@validate_call(materialize_iterators=True)
def create_signature(
    *param_sources: inspect.Parameter | Callable,
    return_source: Any = UNSET,
    excluded_names: Iterable[str] = (),
    accept_double: bool = True,
    replace_double: bool = True,
    include_variadic: bool = True,
    include_binding: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
) -> inspect.Signature:
    """Create a signature from any mix of parameters and callables.

    The sources are merged in the order given and the result is always in a
    valid order.

    Args:
        *param_sources: `inspect.Parameter` objects and callables. A callable
            contributes all of its parameters.
        return_source: `UNSET` for no return annotation, a callable whose return
            annotation is taken, or an annotation itself.
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
        ParamError: If a source is neither a parameter nor a callable, a signature
            cannot be read, a name collision is refused or the order is invalid.
    """

    # 1. Prepare the collector
    collector = ParameterCollector(
        excluded_names = excluded_names,
        accept_double = accept_double,
        replace_double = replace_double,
        include_variadic = include_variadic,
        include_binding = include_binding,
        flat_to_kwargs = flat_to_kwargs,
        _validate_call = False
    )

    # 2. Load parameters from all sources
    load_param_sources(
        collector=collector,
        param_sources=param_sources,
        _validate_call=False
    )

    # 3. Resolve the return annotation
    return_annotation = resolve_return_annotation(
        return_source=return_source,
        _validate_call=False
    )

    # 4. Compose the final signature
    return compose_signature(
        parameters = collector.get_ordered_params(),
        return_annotation = return_annotation,
        _validate_call = False
    )


_DESIGN_NOTES = """
# create_signature — The Universal Entry Point

## Purpose
All other builders are special cases of this one: any number of parameters and
callables go in, one valid signature comes out.

## The Four Steps
| Step | Done by                     | What                                       |
| :--- | :-------------------------- | :----------------------------------------- |
| 1    | `ParameterCollector`        | Created with the exclusion and collision rules. |
| 2    | `load_param_sources`        | Loads every source in the order given.     |
| 3    | `resolve_return_annotation` | Decides the return annotation.             |
| 4    | `compose_signature`         | Builds and validates the result.           |

## Order Is Priority
With `replace_double=True` a later source wins a collision; with `False` the
earlier one stays. The caller controls priority by ordering the sources.

## Collisions Between Variadics
A second `*args` (or `**kwargs`) counts as a collision even under another name,
and is settled by the same rules.

## Trusting Its Own Callers
Every inner call passes `_validate_call=False`. The arguments were checked by
this function's own `@validate_call`.

## Used by
The `signature` decorator.
"""
