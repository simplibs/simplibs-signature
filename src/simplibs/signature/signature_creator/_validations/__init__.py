from .validate_if_sources_or_base_func_is_set import validate_if_sources_or_base_func_is_set
from .validate_is_type_or_callable import validate_is_type_or_callable


_DESIGN_NOTES = """
# signature_creator/_validations

## Contents
Validation functions for `SignatureCreator.__init__()`.

| Name                                      | Description                                                      |
|-------------------------------------------|------------------------------------------------------------------|
| `validate_if_sources_or_base_func_is_set` | Validates that at least one parameter source was provided        |
| `validate_is_type_or_callable`            | Validates that a value is a type or a callable                   |
"""