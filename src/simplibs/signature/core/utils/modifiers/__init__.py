from .add_params_to_signature import add_params_to_signature
from .delete_params_from_signature import delete_params_from_signature
from .replace_return_annotation_in_signature import replace_return_annotation_in_signature


__all__ = [
    "add_params_to_signature",
    "delete_params_from_signature",
    "replace_return_annotation_in_signature",
]


_DESIGN_NOTES = """
# core/utils/modifiers

## Contents
Functions for surgical modifications to existing `inspect.Signature` objects.

| Name                                      | Description                              |
|-------------------------------------------|------------------------------------------|
| `add_params_to_signature`                 | Add parameters to a signature            |
| `delete_params_from_signature`            | Remove parameters by name                |
| `replace_return_annotation_in_signature`  | Update return type annotation            |
"""
