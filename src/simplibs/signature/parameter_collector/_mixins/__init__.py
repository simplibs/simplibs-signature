from .Add import AddMixin
from .GetOrdered import GetOrderedMixin


_DESIGN_NOTES = """
# parameter_collector/_mixins

## Contents
Mixins for `ParameterCollector` — each provides one method.

| Name             | Method          | Description                                              |
|------------------|-----------------|----------------------------------------------------------|
| `AddMixin`       | `add()`         | Sources a parameter with exclusion and duplicate handling   |
| `GetOrderedMixin`| `get_ordered()` | Returns all stored parameters as a flat ordered list     |
"""