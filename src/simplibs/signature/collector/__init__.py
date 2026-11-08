from .ParameterCollector import ParameterCollector


_DESIGN_NOTES = """
# Parameter Collector Sub-Package

## Purpose
Collects parameters from several sources into one valid, ordered set. Every
signature-building operation of the library stands on it. Plain imports, no
`__all__`: the package root decides what is public.

## Internal Components Registry

| Component            | Type        | Description                                              |
| :------------------- | :---------- | :------------------------------------------------------- |
| `ParameterCollector` | Class       | State and public methods of the collector.               |
| `_constants`         | Sub-package | Parameter kinds, storage tiers and bound-parameter names.|
| `_methods`           | Sub-package | The collector's rules as plain functions.                |
"""
