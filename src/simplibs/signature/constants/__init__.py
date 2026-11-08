from .ARGS import ARGS
from .KWARGS import KWARGS


_DESIGN_NOTES = """
# Signature Constants Sub-Package

## Purpose
The two ready-made variadic parameters. Plain imports, no `__all__`: the
package root decides what is public.

## Internal Components Registry

| Component | Type     | Description                                           |
| :-------- | :------- | :---------------------------------------------------- |
| `ARGS`    | Constant | A ready-made `*args` parameter.                       |
| `KWARGS`  | Constant | A ready-made `**kwargs` parameter; flat mode uses it. |
"""
