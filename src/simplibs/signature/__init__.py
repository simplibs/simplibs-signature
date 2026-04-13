from .create_signature import create_signature
from .copy_signature import copy_signature
from .core.signature_creator import SignatureCreator
from .core.parameter_collector import ParameterCollector
from .core.utils import (
    create_positional_parameter,
    create_keyword_parameter,
    get_signature,
    set_signature,
    compose_signature,
    add_params_to_signature,
    delete_params_from_signature,
    replace_return_annotation_in_signature,
)
from .decorators import (
    signature,
    signature_copy,
    signature_set,
    apply_signature_to_wraps,
    create_signature_decorator,
)
from .core.constants import (
    BINDING_NAMES,
    VARIADIC_NAMES,
    ARGS,
    KWARGS,
)
from .core.validators import (
    SignatureError,
    SignatureBuildError,
    SignatureParameterError,
)


__all__ = [
    # Builders
    "create_signature",
    "copy_signature",
    # Decorators
    "signature",
    "signature_copy",
    "signature_set",
    # Creator class
    "SignatureCreator",
    # Parameter class
    "ParameterCollector",
    # Signature operations
    "get_signature",
    "set_signature",
    "compose_signature",
    # Signature modifiers
    "add_params_to_signature",
    "delete_params_from_signature",
    "replace_return_annotation_in_signature",
    # Parameter creators
    "create_positional_parameter",
    "create_keyword_parameter",
    # Decorators utils
    "apply_signature_to_wraps",
    "create_signature_decorator",
    # Constants
    "BINDING_NAMES",
    "VARIADIC_NAMES",
    "ARGS",
    "KWARGS",
    # Validators
    "SignatureError",
    "SignatureBuildError",
    "SignatureParameterError",
]


_DESIGN_NOTES = """
# simplibs.signature

## Purpose
Lightweight utilities for dynamic and declarative function signature manipulation.
Build, copy, merge, and transform `inspect.Signature` objects with a clean API
wrapped in structured exceptions.

## Public API

### Builders (Entry Points)
| Name                | Description                                      |
|---------------------|--------------------------------------------------|
| `create_signature`  | Build signature from scratch or merge sources   |
| `copy_signature`    | Copy and transform an existing signature        |

### Decorators
| Name                | Description                                      |
|---------------------|--------------------------------------------------|
| `@signature`        | Assemble/merge signatures inline                |
| `@signature_copy`   | Copy and transform existing signature as decorator |
| `@signature_set`    | Assign a pre-existing signature directly         |

### Classes
| Name                 | Description                                      |
|----------------------|--------------------------------------------------|
| `SignatureCreator`   | Builder class for complex signature assembly    |
| `ParameterCollector` | Internal manager for parameter grouping/ordering |

### Signature Operations
| Name                | Description                                      |
|---------------------|--------------------------------------------------|
| `get_signature`     | Safely extract signature from callable          |
| `set_signature`     | Assign signature via __signature__              |
| `compose_signature` | Create signature from parameters                |

### Signature Modifiers
| Name                                      | Description                              |
|-------------------------------------------|------------------------------------------|
| `add_params_to_signature`                 | Add parameters to existing signature     |
| `delete_params_from_signature`            | Remove parameters by name                |
| `replace_return_annotation_in_signature`  | Update return type annotation            |

### Parameter Creators
| Name                          | Description                              |
|-------------------------------|------------------------------------------|
| `create_positional_parameter` | Factory for positional parameters       |
| `create_keyword_parameter`    | Factory for keyword-only parameters     |

### Decorator Utilities
| Name                        | Description                                      |
|-----------------------------|--------------------------------------------------|
| `apply_signature_to_wraps`  | Create wrapper with custom signature + async support |
| `create_signature_decorator`| Convert signature into reusable decorator       |

### Constants
| Name              | Type      | Description                        |
|-------------------|-----------|-----------------------------------|
| `BINDING_NAMES`   | frozenset | {'self', 'cls'} — binding params   |
| `VARIADIC_NAMES`  | frozenset | {'args', 'kwargs'} — variadic names|
| `ARGS`            | Parameter | Pre-built *args (VAR_POSITIONAL)   |
| `KWARGS`          | Parameter | Pre-built **kwargs (VAR_KEYWORD)   |

### Exceptions
| Name                        | Description                              |
|-----------------------------|------------------------------------------|
| `SignatureError`            | Base — catches all signature errors     |
| `SignatureBuildError`       | Signature assembly failed                |
| `SignatureParameterError`   | Invalid argument type                    |

## Module Structure

```
simplibs/signature/
├── core/                      # Internal implementations
│   ├── constants/             # Pre-built parameters and sentinel sets
│   ├── parameter_collector/   # Parameter grouping engine
│   ├── signature_creator/     # Builder class and mixins
│   ├── utils/                 # User-facing utilities
│   └── validators/            # Validation and exceptions
├── decorators/                # Decorator implementations
├── create_signature.py        # Main entry point (builder)
├── copy_signature.py          # Secondary entry point (transformer)
└── __init__.py                # This file — public API
```

## Quick Examples

### Copy and transform
```python
@signature_copy(MyClass.__init__, returns=MyClass)
def create(*args, **kwargs):
    return MyClass(*args, **kwargs)
```

### Merge signatures
```python
@signature(extra_param, use_func=True, func_first=True)
def handler(request):
    ...
```

### Build from scratch
```python
sig = create_signature(param1, param2, my_func)
```

### Manual operations
```python
sig = get_signature(my_func)
sig = add_params_to_signature(sig, (new_param,))
set_signature(wrapper_func, sig)
```
"""
