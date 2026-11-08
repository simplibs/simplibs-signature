import inspect
# Outers
from .._constants.strings import WITHOUT_DEFAULT, CONTAIN_DEFAULT
from .._constants.kinds import EMPTY, VAR_POSITIONAL, VAR_KEYWORD
# Inners
from ._positional_empty_order_check import _positional_empty_order_check
from ._find_colliding_name import _find_colliding_name
from ._flat_params_to_kwargs import _flat_params_to_kwargs
from ._remove_param import _remove_param
from .validations import (
    raise_duplicate_parameter_error,
    raise_invalid_parameter_kind_error,
)


def add_param(
    param: inspect.Parameter,
    excluded_names: set[str],
    include_variadic: bool,
    flat_to_kwargs: bool,
    accept_double: bool,
    replace_double: bool,
    seen_names: dict[str, tuple[inspect._ParameterKind, str]],
    params_map: dict[inspect._ParameterKind, dict[str, list[inspect.Parameter]]]
) -> None:
    """Store one parameter, subject to the exclusion, collision and order rules.

    Args:
        param: The parameter to store.
        excluded_names: Names to leave out.
        include_variadic: If False, `*args` and `**kwargs` are left out by kind.
        flat_to_kwargs: Flat mode: store everything as keyword-only.
        accept_double: If False, a collision raises.
        replace_double: True: the new parameter replaces the stored one.
            False: the stored one stays.
        seen_names: The name index (changed in place).
        params_map: The tiered storage (changed in place).

    Raises:
        ParamError: On a refused collision, a required positional parameter
            after an optional one, or a kind that cannot be stored.
    """

    # 1. Exclusion by name (the caller's names, `self` and `cls`)
    if param.name in excluded_names:
        return

    # 2. Exclusion by kind: a variadic is recognised by what it is, not by its name
    if not include_variadic and param.kind in (VAR_POSITIONAL, VAR_KEYWORD):
        return

    # 3. Flat mode has its own storage rules
    if flat_to_kwargs:
        _flat_params_to_kwargs(
            param=param,
            params_map=params_map,
            seen_names=seen_names,
            accept_double=accept_double,
            replace_double=replace_double
        )
        return

    # 4. Collision: the same name, or a second variadic of a kind already stored
    colliding_name = _find_colliding_name(param, seen_names, params_map)
    if colliding_name is not None:

        # 4.1 Strict: a collision is an error
        if not accept_double:
            raise_duplicate_parameter_error(param, colliding_name)

        # 4.2 The original stays, the new parameter is dropped
        if not replace_double:
            return

        # 4.3 The new parameter replaces the stored one
        _remove_param(colliding_name, seen_names, params_map)

    # 5. A required positional parameter may not follow an optional one
    _positional_empty_order_check(param, params_map)

    # 6. Pick the tier: with or without a default
    inner_key = WITHOUT_DEFAULT if param.default is EMPTY else CONTAIN_DEFAULT

    # 7. Store it
    try:
        params_map[param.kind][inner_key].append(param)

    # 8. A kind the storage map does not know
    except KeyError as e:
        raise_invalid_parameter_kind_error(param, e)

    # 9. Index the name
    seen_names[param.name] = (param.kind, inner_key)


_DESIGN_NOTES = """
# add_param — The Single Entry Door of the Collector

## Purpose
Every parameter that reaches the collector goes through this function, and it
decides in a fixed order what happens to it. `ParameterCollector.add_param` only
passes its state in.

## The Order
1. Names the caller excluded, `self` and `cls` are dropped.
2. Variadics are dropped if `include_variadic=False`.
3. Flat mode takes over.
4. A collision is refused, resolved in favour of the old or the new.
5. A required positional parameter after an optional one is refused.
6. The parameter is stored in its kind and tier, and its name is indexed.

## Variadics by Kind
Names do not identify a variadic: `*a` and `**options` are as variadic as
`*args`. `include_variadic=False` therefore looks at the kind. `self` and `cls`
have no kind of their own, so they stay a matter of names (`BINDING_NAMES`).

## Why Exclusion Comes First
An excluded parameter must leave no trace: no collision, no order check, no
renaming in flat mode.

## Where an Error Points
Every error here is a `ParamError`; see the notes of the package root.
"""
