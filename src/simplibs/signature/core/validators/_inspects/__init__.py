from .validate_is_inspect_parameter import validate_is_inspect_parameter
from .validate_is_inspect_signature import validate_is_inspect_signature
from .validate_parameters_collection import validate_parameters_collection


__all__ = [
    "validate_is_inspect_parameter",
    "validate_is_inspect_signature",
    "validate_parameters_collection",
]


_DESIGN_NOTES = """
# core/validators/_inspects

## Contents
Validation for standard objects from the `inspect` module.

| Name                             | Description                                   |
|----------------------------------|-----------------------------------------------|
| `validate_is_inspect_parameter`  | Validates an inspect.Parameter instance       |
| `validate_is_inspect_signature`  | Validates an inspect.Signature instance       |
| `validate_parameters_collection` | Validates a collection of inspect.Parameters  |
"""