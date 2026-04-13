from .validate_default_matches_annotation import validate_default_matches_annotation
from .validate_param_sources import validate_param_sources


__all__ = [
    "validate_default_matches_annotation",
    "validate_param_sources",
]


_DESIGN_NOTES = """
# core/validators/_rules

## Contents
Enforces Python's signature logic and library-specific structural rules.

| Name                                  | Description                                      |
|---------------------------------------|--------------------------------------------------|
| `validate_default_matches_annotation` | Ensures default value type matches type hint     |
| `validate_param_sources`              | Validates list of parameters or callables        |
"""