from .load_param_sources import load_param_sources
from .resolve_return_annotation import resolve_return_annotation


_DESIGN_NOTES = """
# Orchestrator Helpers Sub-Package

## Purpose
The two preparatory steps of `create_signature`. Plain imports, no `__all__`:
the package root decides what is public.

## Internal Components Registry

| Component                  | Type        | Description                                             |
| :------------------------- | :---------- | :------------------------------------------------------ |
| `load_param_sources`       | Function    | Feeds parameters and callables into a collector.        |
| `resolve_return_annotation`| Function    | Turns a return source into an annotation.               |
| `_validations`             | Sub-package | The error of `load_param_sources`.                      |
"""
