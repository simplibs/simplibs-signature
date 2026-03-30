from .signature_copy import signature_copy
from .signature_from import signature_from


_DESIGN_NOTES = """
# signature_decorators

## Contents
The primary public interface of the library — two decorators for the most
common signature manipulation scenarios.

| Name              | Description                                                              |
|-------------------|--------------------------------------------------------------------------|
| `signature_copy`  | Copies and normalises a signature from an existing callable              |
| `signature_from`  | Assembles a new signature from the decorated function and additional sources |

## Usage
```python
@signature_copy(MyClass.__init__, return_type=MyClass)
def create(*args, **kwargs): ...

@signature_from(extra_param, base_func_first=False)
def my_func(*args, **kwargs): ...
```
"""