from ._primitives import (
    validate_is_bool,
    validate_is_callable,
    validate_is_string,
)
from ._inspects import (
    validate_is_inspect_parameter,
    validate_is_inspect_signature,
    validate_parameters_collection,
)
from ._rules import (
    validate_default_matches_annotation,
    validate_param_sources,
)
from ._policies import (
    validate_accept_double,
    validate_excluded_names,
)
from .exceptions import (
    SignatureError,
    SignatureBuildError,
    SignatureParameterError,
)

__all__ = [
    # Primitives
    "validate_is_bool",
    "validate_is_callable",
    "validate_is_string",
    # Inspect
    "validate_is_inspect_parameter",
    "validate_is_inspect_signature",
    "validate_parameters_collection",
    # Rules
    "validate_default_matches_annotation",
    "validate_param_sources",
    # Policies
    "validate_accept_double",
    "validate_excluded_names",
    # Exceptions
    "SignatureError",
    "SignatureBuildError",
    "SignatureParameterError",
]

_DESIGN_NOTES = """
# core/validators

## Contents
Validation functions and exception classes for the signature library.

### Validators

#### Primitives (basic reusable type checks)
| Name                    | Category    | Description                                  |
|-------------------------|-------------|----------------------------------------------|
| `validate_is_bool`      | primitives  | Validates bool type                          |
| `validate_is_callable`  | primitives  | Validates callability                        |
| `validate_is_string`    | primitives  | Validates string type                        |

#### Inspect Types (inspect API validation)
| Name                              | Category        | Description                                  |
|-----------------------------------|------------------|----------------------------------------------|
| `validate_is_inspect_parameter`   | inspect_types    | Validates inspect.Parameter instance         |
| `validate_is_inspect_signature`  | inspect_types    | Validates inspect.Signature instance         |
| `validate_parameters_collection` | inspect_types    | Validates iterable of Parameters             |

#### Rules (Python signature semantics)
| Name                                   | Category | Description                                  |
|----------------------------------------|----------|----------------------------------------------|
| `validate_default_matches_annotation`  | rules    | Validates default matches annotation         |
| `validate_param_sources`               | rules    | Validates parameter/callable sources         |
| `validate_variadic_has_no_default`     | rules    | Ensures variadic params have no default      |

#### Policies (library-specific behavior)
| Name                        | Category  | Description                                  |
|-----------------------------|-----------|----------------------------------------------|
| `validate_accept_double`    | policies  | Validates duplicate parameter handling       |
| `validate_excluded_names`   | policies  | Validates excluded parameter names           |

### Exceptions
| Name                        | Description                                   |
|-----------------------------|-----------------------------------------------|
| `SignatureError`            | Base exception — catch all signature errors   |
| `SignatureBuildError`       | Signature assembly failed                    |
| `SignatureParameterError`   | Invalid argument type                        |
"""
