import inspect
from typing import Self


class GetOrderedMixin:
    """Mixin for retrieving stored parameters in the correct inspect-defined order."""

    def get_ordered(self: Self) -> list[inspect.Parameter]:
        """
        Returns all stored parameters as a flat list ordered by kind.

        Order follows inspect._ParameterKind:
            1) POSITIONAL_ONLY
            2) POSITIONAL_OR_KEYWORD
            3) VAR_POSITIONAL
            4) KEYWORD_ONLY
            5) VAR_KEYWORD
        """
        return [
            param
            for params in self._param_list.values()
            for param in params
        ]


_DESIGN_NOTES = """
# GetOrderedMixin

## Purpose
Provides the `get_ordered()` method for `ParameterCollector` — flattens the
internal `_param_list` dictionary into a single ordered list of parameters.

## Why the order is guaranteed
`_param_list` is a regular `dict` keyed by `inspect._ParameterKind` values,
inserted in the correct kind order during `ParameterCollector.__init__()`.
Python dicts preserve insertion order (3.7+), so iterating `.values()` always
yields the kinds in the correct sequence — no explicit sorting needed.

## Notes
- The list comprehension flattens one level — each value in `_param_list`
  is a list of parameters for that kind, and all are concatenated in order.
- Returns an empty list if no parameters have been added yet.
"""