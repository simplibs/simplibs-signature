from .SignatureError import SignatureError
from .SignatureBuildError import SignatureBuildError
from .SignatureParameterError import SignatureParameterError


_DESIGN_NOTES = """
# utils/_validations/base

## Contents
The exception hierarchy for the `simple-signature` library.

| Name                     | Description                                                    |
|--------------------------|----------------------------------------------------------------|
| `SignatureError`         | Base — catches all `simple-signature` errors                   |
| `SignatureParameterError`| Raised when an invalid argument type is passed by the user     |
| `SignatureBuildError`    | Raised when a signature cannot be built at runtime             |

## Hierarchy
    SignatureError
    ├── SignatureParameterError
    └── SignatureBuildError
"""