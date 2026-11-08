from .copy_signature import copy_signature
from .create_signature import create_signature


_DESIGN_NOTES = """
# Signature Orchestrators Sub-Package

## Purpose
The high-level builders. They combine the collector with the tools into one
call. Plain imports, no `__all__`: the package root decides what is public.

## Internal Components Registry

| Component          | Type        | Description                                              |
| :----------------- | :---------- | :------------------------------------------------------- |
| `copy_signature`   | Function    | A changed copy of one callable's signature.              |
| `create_signature` | Function    | A signature from any mix of parameters and callables.    |
| `_helpers`         | Sub-package | Loading of sources and the return annotation.            |
"""
