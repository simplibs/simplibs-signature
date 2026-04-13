from .validate_accept_double import validate_accept_double
from .validate_excluded_names import validate_excluded_names


__all__ = [
    "validate_accept_double",
    "validate_excluded_names",
]


_DESIGN_NOTES = """
# core/validators/_policies

## Contents
Validations related to library configuration and behavior policies.

| Name                       | Description                                         |
|----------------------------|-----------------------------------------------------|
| `validate_accept_double`   | Validates name uniqueness based on user policy      |
| `validate_excluded_names`  | Validates collection of names to be ignored         |
"""