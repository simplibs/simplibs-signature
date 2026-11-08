import inspect
from typing import Iterable
from simplibs.validate import validate_call
# Outers
from ...collector import ParameterCollector


@validate_call(materialize_iterators=True)
def delete_params_from_signature(
    signature: inspect.Signature,
    excluded_names: Iterable[str],
    *,
    _validate_call: bool = True
) -> inspect.Signature:
    """Create a new signature without the named parameters.

    Names that are not in the signature are ignored. The original signature
    is not changed.

    Args:
        signature: The signature to start from.
        excluded_names: The names of the parameters to remove.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Returns:
        A new `inspect.Signature` without the excluded parameters.
    """

    # 1. Initialize collector with exclusion rules
    collector = ParameterCollector(
        excluded_names=excluded_names,
        _validate_call=False,
    )

    # 2. Load signature parameters into the collector
    collector.add_params(
        params=signature.parameters.values(),
        _validate_call=False
    )

    # 3. Retrieve the filtered and ordered parameters
    new_params = collector.get_ordered_params()

    # 4. Construct and return the new signature
    return signature.replace(
        parameters=new_params
    )


_DESIGN_NOTES = """
# delete_params_from_signature — Remove Parameters by Name

## Purpose
The collector already knows how to leave names out, so deleting is "load the
signature, with these names excluded".

## What Stays
The return annotation and every parameter that was not named, in the order
Python requires. Removing a parameter can never break the order, so no error
is possible for the order.

## Unknown Names Are Fine
Excluding a name that is not there does nothing. A delete that has nothing to
delete is already in the state the caller asked for.

## Other Collector Options
Not offered: nothing but the named parameters is meant to change.
"""
