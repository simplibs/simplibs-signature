from .parameters import create_positional_parameter, create_keyword_parameter
from .operations import get_signature, set_signature, compose_signature
from .modifiers import (
    add_params_to_signature,
    delete_params_from_signature,
    replace_return_annotation_in_signature,
)


__all__ = [
    # Parameters
    "create_positional_parameter",
    "create_keyword_parameter",
    # Operations
    "get_signature",
    "set_signature",
    "compose_signature",
    # Modifiers
    "add_params_to_signature",
    "delete_params_from_signature",
    "replace_return_annotation_in_signature",
]


_DESIGN_NOTES = """
# core/utils

## Contents
User-facing utility functions for signature and parameter manipulation.

### Parameter Creation
| Name                          | Description                              |
|-------------------------------|------------------------------------------|
| `create_positional_parameter` | Factory for positional parameters       |
| `create_keyword_parameter`    | Factory for keyword-only parameters     |

### Signature Operations
| Name                | Description                                   |
|---------------------|-----------------------------------------------|
| `get_signature`     | Extract signature from callable               |
| `set_signature`     | Assign signature via __signature__            |
| `compose_signature` | Create signature from parameters              |

### Signature Modifiers
| Name                                      | Description                              |
|-------------------------------------------|------------------------------------------|
| `add_params_to_signature`                 | Add parameters to existing signature     |
| `delete_params_from_signature`            | Remove parameters from signature         |
| `replace_return_annotation_in_signature`  | Update return type                       |
"""
