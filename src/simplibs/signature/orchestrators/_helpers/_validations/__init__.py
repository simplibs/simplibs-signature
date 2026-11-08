from .raise_invalid_parameter_source_error import raise_invalid_parameter_source_error


_DESIGN_NOTES = """
# Orchestrator Helper Validations Sub-Package

## Purpose
The error of `load_param_sources`. Plain imports, no `__all__`: the package
root decides what is public.

## Internal Components Registry

| Component                              | Type     | Description                                         |
| :------------------------------------- | :------- | :-------------------------------------------------- |
| `raise_invalid_parameter_source_error` | Function | A source is neither a parameter nor a callable.     |
"""
