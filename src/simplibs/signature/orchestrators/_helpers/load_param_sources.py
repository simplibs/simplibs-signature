import inspect
from typing import Callable
from simplibs.validate import validate_call
# Outers
from ...collector import ParameterCollector
from ...tools.operations import get_signature
# Inners
from ._validations import raise_invalid_parameter_source_error


@validate_call
def load_param_sources(
    collector: ParameterCollector,
    param_sources: tuple[inspect.Parameter | Callable, ...],
    *,
    _validate_call: bool = True
) -> None:
    """Load the parameters of every source into a collector.

    Args:
        collector: The collector to fill.
        param_sources: Parameters and callables, in the order they are loaded.
        _validate_call: Reserved switch of `@validate_call`. False skips the
            validation of the arguments; trusted internal callers pass it.

    Raises:
        ParamError: If a source is neither a parameter nor a callable, or if
            the collector refuses a parameter.
    """

    for index, item in enumerate(param_sources):

        # 1. A Parameter goes straight into the collector
        if isinstance(item, inspect.Parameter):
            collector.add_param(
                param=item,
                _validate_call=False
            )

        # 2. A callable contributes all of its parameters
        elif callable(item):
            signature = get_signature(
                function=item,
                _validate_call=False
            )
            collector.add_params(
                params=signature.parameters.values(),
                _validate_call=False
            )

        # 3. Anything else is an invalid source
        else:
            raise_invalid_parameter_source_error(index, item)


_DESIGN_NOTES = """
# load_param_sources — Turn Mixed Sources Into Collector Input

## Purpose
`create_signature` accepts parameters and callables side by side. This
function is the one place that tells them apart and feeds the collector.

## Order Is the Order Given
Sources are loaded one after another, so with `replace_double=True` a later
source wins a name collision. The caller controls priority by ordering.

## `Parameter` Before `callable`
An `inspect.Parameter` is not callable, but the order of the checks makes that
independent of any future change. Anything that is neither is an error naming
the position of the offender.
"""
