from .validate_default_matches_annotation import validate_default_matches_annotation


_DESIGN_NOTES = """
# Parameter Validations Sub-Package

## Purpose
The sanity check behind the parameter creators. Plain imports, no `__all__`:
the package root decides what is public.

## Internal Components Registry

| Component                             | Type     | Description                                        |
| :------------------------------------ | :------- | :------------------------------------------------- |
| `validate_default_matches_annotation` | Function | A default must fit a plain class annotation.       |
"""
