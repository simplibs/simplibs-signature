from .groups import BINDING_NAMES
from .kinds import (
    EMPTY,
    KEYWORD_ONLY,
    POSITIONAL_ONLY,
    POSITIONAL_OR_KEYWORD,
    VAR_KEYWORD,
    VAR_POSITIONAL,
)
from .strings import (
    CONTAIN_DEFAULT,
    WITHOUT_DEFAULT,
)


_DESIGN_NOTES = """
# Collector Constants Sub-Package

## Purpose
The fixed vocabulary of the collector: parameter kinds, storage tiers and the
names of bound parameters. Plain imports, no `__all__`: the package root
decides what is public.

## Internal Components Registry

| Component | Type        | Description                                              |
| :-------- | :---------- | :------------------------------------------------------- |
| `groups`  | Sub-package | `BINDING_NAMES`, the names excluded as a group.          |
| `kinds`   | Sub-package | The five parameter kinds and the `EMPTY` marker.         |
| `strings` | Sub-package | The two storage tiers, with and without a default.       |
"""
