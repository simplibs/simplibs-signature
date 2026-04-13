from .AddParam import AddParamMixin
from .GetOrderedParams import GetOrderedParamsMixin
from .FlatParamsToKwarks import FlatParamsToKwarksMixin
from .PositionalEmptyOrderCheck import PositionalEmptyOrderCheckMixin

__all__ = [
    "AddParamMixin",
    "GetOrderedParamsMixin",
    "FlatParamsToKwarksMixin",
    "PositionalEmptyOrderCheckMixin",
]


_DESIGN_NOTES = """
# core/parameter_collector/_mixins

## Contents
Functional mixins for the `ParameterCollector`. Each mixin is dedicated to a 
specific part of the parameter lifecycle to keep the main class clean and 
focused.

| Name                             | Method                           | Description                                           |
|----------------------------------|----------------------------------|-------------------------------------------------------|
| `AddParamMixin`                  | `add_param()`                    | Primary logic for adding and deduplicating parameters. |
| `GetOrderedParamsMixin`          | `get_ordered_params()`           | Assembly logic to return parameters in legal order.   |
| `FlatParamsToKwarksMixin`        | `_flat_params_to_kwargs()`       | Logic for transforming parameters in "Flat Mode".     |
| `PositionalEmptyOrderCheckMixin` | `_positional_empty_order_check()`| Enforces Python's mandatory-before-optional rule.    |
"""