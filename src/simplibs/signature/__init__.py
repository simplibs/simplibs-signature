"""
simple_signature

Lightweight utilities for dynamic and declarative function signature manipulation.
"""
from .signature_decorators import signature_copy, signature_from
from .signature_decorators.utils import apply_signature_to_wraps, create_signature_decorator
from .signature_creator import SignatureCreator, create_signature
from .utils.signatures import get_signature, set_signature, create_copy_signature
from .utils.parameters import create_positional_parameter, create_keyword_parameter
from .parameter_collector import ParameterCollector
from .utils.constants import ARGS, KWARGS, EXCLUDED


__all__ = [
    # Decorators
    "signature_copy",
    "signature_from",
    # Decorators utils
    "apply_signature_to_wraps",
    "create_signature_decorator",
    # Signature creators
    "SignatureCreator",
    "create_signature",
    # Signature operations
    "get_signature",
    "set_signature",
    "create_copy_signature",
    # Parameter creators
    "create_positional_parameter",
    "create_keyword_parameter",
    # Parameter class
    "ParameterCollector",
    # Constants
    "ARGS",
    "KWARGS",
    "EXCLUDED",
]


_DESIGN_NOTES = """
# simple_signature

## Public API

### Decorators
| Name                        | Description                                                              |
|-----------------------------|--------------------------------------------------------------------------|
| `signature_copy`            | Copies and normalises a signature from an existing callable              |
| `signature_from`            | Assembles a new signature from the decorated function and additional sources |

### Decorator utils
| Name                        | Description                                                              |
|-----------------------------|--------------------------------------------------------------------------|
| `apply_signature_to_wraps`  | Creates a new wrapper around a function with an assigned signature       |
| `create_signature_decorator`| Produces a reusable decorator from an `inspect.Signature`                |

### Signature creators
| Name               | Description                                                              |
|--------------------|--------------------------------------------------------------------------|
| `SignatureCreator` | Builder class — assembles a signature from any combination of sources    |
| `create_signature` | Functional interface — identical parameters, returns the signature directly |

### Signature operations
| Name                    | Description                                                         |
|-------------------------|---------------------------------------------------------------------|
| `get_signature`         | Safely retrieves an `inspect.Signature` from a callable             |
| `set_signature`         | Assigns an `inspect.Signature` directly to a function               |
| `create_copy_signature` | Creates a modified copy of a signature from a callable              |

### Parameter creators
| Name                          | Description                                                   |
|-------------------------------|---------------------------------------------------------------|
| `create_positional_parameter` | Creates a `POSITIONAL_ONLY` or `POSITIONAL_OR_KEYWORD` parameter |
| `create_keyword_parameter`    | Creates a `KEYWORD_ONLY` parameter                            |

### Parameter class
| Name                 | Description                                                          |
|----------------------|----------------------------------------------------------------------|
| `ParameterCollector` | Stores and manages parameters grouped by kind                        |

### Constants
| Name       | Description                                      |
|------------|--------------------------------------------------|
| `ARGS`     | Pre-built `*args` parameter (VAR_POSITIONAL)     |
| `KWARGS`   | Pre-built `**kwargs` parameter (VAR_KEYWORD)     |
| `EXCLUDED` | Default exclusion set — `{"self", "cls"}`        |
"""