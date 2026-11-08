from .CONTAIN_DEFAULT import CONTAIN_DEFAULT
from .WITHOUT_DEFAULT import WITHOUT_DEFAULT


_DESIGN_NOTES = """
# Collector Tier Constants Sub-Package

## Purpose
The two keys that split every kind of the storage map into required and
optional parameters. Plain imports, no `__all__`: the package root decides
what is public.

## Internal Components Registry

| Component         | Type     | Description                                |
| :---------------- | :------- | :----------------------------------------- |
| `CONTAIN_DEFAULT` | Constant | Tier of parameters with a default value.   |
| `WITHOUT_DEFAULT` | Constant | Tier of parameters without a default value.|
"""
