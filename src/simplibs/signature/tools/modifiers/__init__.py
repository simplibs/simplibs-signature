from .add_params_to_signature import add_params_to_signature
from .delete_params_from_signature import delete_params_from_signature
from .replace_return_annotation_in_signature import replace_return_annotation_in_signature


_DESIGN_NOTES = """
# Signature Modifiers Sub-Package

## Purpose
Take a signature, return a changed copy: add parameters, delete parameters,
replace the return annotation. The original is never touched. Plain imports, no
`__all__`: the package root decides what is public.

## Internal Components Registry

| Component                                | Type        | Description                                    |
| :--------------------------------------- | :---------- | :--------------------------------------------- |
| `add_params_to_signature`                | Function    | Adds parameters and keeps the order valid.     |
| `delete_params_from_signature`           | Function    | Removes parameters by name.                    |
| `replace_return_annotation_in_signature` | Function    | Changes only the return annotation.            |
| `_validations`                           | Sub-package | The errors of `add_params_to_signature`.       |
"""
