from .BINDING_NAMES import BINDING_NAMES


_DESIGN_NOTES = """
# Collector Group Constants Sub-Package

## Purpose
Sets of names the collector can exclude as a group. Plain imports, no
`__all__`: the package root decides what is public.

## Internal Components Registry

| Component       | Type     | Description                                  |
| :-------------- | :------- | :------------------------------------------- |
| `BINDING_NAMES` | Constant | `self` and `cls`, as an immutable set.       |
"""
