import inspect
from typing import Iterable
from simplibs.validate import validate_call
# Outers
from ...collector import ParameterCollector
# Inners
from ._validations import (
    raise_signature_type_error,
    raise_signature_structure_value_error
)


@validate_call(materialize_iterators=True)
def add_params_to_signature(
    signature: inspect.Signature,
    params_to_add: Iterable[inspect.Parameter],
    *,
    accept_double: bool = True,
    replace_double: bool = True,
    flat_to_kwargs: bool = False,
    _validate_call: bool = True
) -> inspect.Signature:
    """Create a new signature by adding parameters to an existing one.

    The result is always in a valid order, whatever the order of the input.
    The original signature is not changed.

    Args:
        signature: The signature to start from.
        params_to_add: The parameters to add.
        accept_double: If False, a name collision raises `ParamError`. If True,
            `replace_double` decides who wins.
        replace_double: True: the later parameter replaces the earlier one.
            False: the earlier one stays. In flat mode the later one is kept as
            well, renamed to `name_1`, `name_2`, ...
        flat_to_kwargs: If True, every parameter becomes keyword-only; `*args`
            is dropped and all `**kwargs` merge into one.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        A new `inspect.Signature` with the merged, ordered parameters.

    Raises:
        ParamError: On a refused name collision, a required positional parameter
            after an optional one, or a structure `inspect` rejects.
    """

    # 1. Read the new parameters once: a generator would be empty for the error message
    params_to_add = tuple(params_to_add)

    # 2. Initialize collector with duplicate handling rules
    param_collector = ParameterCollector(
        accept_double=accept_double,
        replace_double=replace_double,
        flat_to_kwargs=flat_to_kwargs,
        _validate_call=False,  # Parameters already validated or trusted
    )

    # 3. Load existing signature parameters into the collector
    param_collector.add_params(
        params=signature.parameters.values(),
        _validate_call=False
    )

    # 4. Add new parameters to the collector
    param_collector.add_params(
        params=params_to_add,
        _validate_call=False
    )

    # 5. Get ordered parameters
    ordered_params = param_collector.get_ordered_params()

    # 6. Construct the new signature from ordered parameters
    try:
        return signature.replace(
            parameters=ordered_params
        )

    # 7. Handle structural issues
    except ValueError as e:
        raise_signature_structure_value_error(params_to_add, e)

    # 8. Handle type mismatches during replacement
    except TypeError as e:
        raise_signature_type_error(ordered_params, e)


_DESIGN_NOTES = """
# add_params_to_signature — Merge New Parameters Into a Signature

## Purpose
Adding a parameter by hand means finding its place: after the required ones,
before `*args`, never after `**kwargs`. The function hands that to the
collector, so the caller only says *what* to add.

## Order of Loading
The existing parameters go in first, the new ones second. With the default
`replace_double=True` a new parameter replaces an existing one of the same name;
with `False` the existing one stays.

## Only Three Options
`include_variadic` and `include_binding` are not offered: the signature is
taken as it is, nothing is meant to disappear from it.

## `signature.replace`
The result is made with `signature.replace(parameters=...)`, which keeps the
return annotation of the original.

## Materialised Once
`params_to_add` may be a generator. It is read into a tuple first, so the
collector and the error message see the same parameters.

## Defensive Branches
The collector already refuses duplicates and wrong order, so `inspect` rarely
has anything left to object to. The two `except` branches stay for the cases
nobody foresaw. The tests reach them by replacing the collector's
`get_ordered_params`.
"""
