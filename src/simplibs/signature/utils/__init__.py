from .constants import ARGS, KWARGS, EXCLUDED
from .parameters import create_keyword_parameter, create_positional_parameter
from .signatures import get_signature, set_signature, create_copy_signature
from ._validations import (
    # Base classes
    SignatureError,
    SignatureBuildError,
    SignatureParameterError,
    # Validators
    validate_is_type,
    validate_is_string,
    validate_is_callable,
    validate_is_bool,
    validate_is_inspect_signature,
)


_DESIGN_NOTES = """
# utils

## Contents
The internal utility layer of the library — constants, parameter factories,
signature operations, exceptions, and validators.

### Constants
| Name       | Description                                      |
|------------|--------------------------------------------------|
| `ARGS`     | Pre-built `*args` parameter (VAR_POSITIONAL)     |
| `KWARGS`   | Pre-built `**kwargs` parameter (VAR_KEYWORD)     |
| `EXCLUDED` | Default exclusion set — `{"self", "cls"}`        |

### Parameter factories
| Name                          | Description                                          |
|-------------------------------|------------------------------------------------------|
| `create_positional_parameter` | Creates a `POSITIONAL_ONLY` or `POSITIONAL_OR_KEYWORD` parameter |
| `create_keyword_parameter`    | Creates a `KEYWORD_ONLY` parameter                   |

### Signature operations
| Name                    | Description                                               |
|-------------------------|-----------------------------------------------------------|
| `get_signature`         | Safely retrieves an `inspect.Signature` from a callable   |
| `set_signature`         | Assigns an `inspect.Signature` directly to a function     |
| `create_copy_signature` | Creates a modified copy of a signature from a callable    |

### Exceptions
| Name                      | Description                                              |
|---------------------------|----------------------------------------------------------|
| `SignatureError`          | Base — catches all `simple-signature` errors             |
| `SignatureParameterError` | Raised when an invalid argument type is passed by the user |
| `SignatureBuildError`     | Raised when a signature cannot be built at runtime       |

### Validators
| Name                           | Description                                         |
|--------------------------------|-----------------------------------------------------|
| `validate_is_bool`             | Validates that a value is a `bool`                  |
| `validate_is_callable`         | Validates that a value is callable                  |
| `validate_is_string`           | Validates that a value is a `str`                   |
| `validate_is_type`             | Validates that a value is a type (class)            |
| `validate_is_inspect_signature`| Validates that a value is an `inspect.Signature`    |
"""