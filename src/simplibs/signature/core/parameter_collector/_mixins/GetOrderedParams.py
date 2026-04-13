import inspect
from typing import Self


class GetOrderedParamsMixin:
    """Mixin for retrieving stored parameters in the correct inspect-defined order."""

    def get_ordered_params(self: Self) -> tuple[inspect.Parameter, ...]:
        """
        Returns all stored parameters as a tuple ordered by parameter kind.

        Flattens the two-tiered internal storage (kind -> category) into a
        single linear sequence that respects Python's syntactic rules.

        Returns:
            A tuple of all stored parameters in valid order.
        """
        return tuple(
            param
            for category_map in self._params_map.values()
            for param_list in category_map.values()
            for param in param_list
        )


_DESIGN_NOTES = """
# GetOrderedParamsMixin

## Purpose
Provides the `get_ordered_params()` method for `ParameterCollector`. It flattens
the complex internal two-tiered storage into a single tuple ready for 
consumption by `inspect.Signature`.

## Why the Order is Guaranteed
The integrity of the resulting signature order relies on two structural layers:

1. **Kind Order**: The `_params_map` is initialized as a dictionary with keys 
   inserted in the strict legal sequence of `inspect._ParameterKind`. Python 
   dictionaries preserve this insertion order.
2. **Category Order**: Within each kind, we store parameters in a nested 
   dictionary: `{_WITHOUT_DEFAULT: [], _CONTAIN_DEFAULT: []}`. 
   By iterating over `.values()` of this nested dictionary, we naturally 
   yield mandatory parameters (no default) before optional ones (with default).

## Process Flow
The method uses a triple-nested generator expression:
- **Outer loop**: Iterates through parameter kinds (Positional -> Keyword -> Variadic).
- **Middle loop**: Iterates through the two categories (Non-default list -> Default list).
- **Inner loop**: Yields the individual `inspect.Parameter` objects.

## Performance Characteristics
- **Time Complexity**: O(N) where N is the total number of parameters stored.
- **Space Complexity**: O(N) for the output tuple.
- **Efficiency**: Uses a single-pass flatting strategy which is memory-efficient 
  before the final tuple materialization.

## Notes
- This method is the "assembly line" that prepares the data for the final 
  Signature object.
- It assumes that `AddParamMixin` has already performed all necessary 
  validation; this mixin is purely for transformation/output.
"""