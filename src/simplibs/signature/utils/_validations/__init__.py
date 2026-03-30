from .exceptions import SignatureError, SignatureBuildError, SignatureParameterError

from .validate_is_bool import validate_is_bool
from .validate_is_callable import validate_is_callable
from .validate_is_string import validate_is_string
from .validate_is_type import validate_is_type
from .validate_is_inspect_signature import validate_is_inspect_signature


_DESIGN_NOTES = """
# utils/_validations

## Contents
Exception hierarchy and validation functions shared across the library.

### Exceptions
| Name                      | Description                                              |
|---------------------------|----------------------------------------------------------|
| `SignatureError`          | Base — catches all `simple-signature` errors             |
| `SignatureParameterError` | Raised when an invalid argument type is passed by the user |
| `SignatureBuildError`     | Raised when a signature cannot be built at runtime       |

### Validations
| Name                           | Description                                         |
|--------------------------------|-----------------------------------------------------|
| `validate_is_bool`             | Validates that a value is a `bool`                  |
| `validate_is_callable`         | Validates that a value is callable                  |
| `validate_is_string`           | Validates that a value is a `str`                   |
| `validate_is_type`             | Validates that a value is a type (class)            |
| `validate_is_inspect_signature`| Validates that a value is an `inspect.Signature`    |
"""