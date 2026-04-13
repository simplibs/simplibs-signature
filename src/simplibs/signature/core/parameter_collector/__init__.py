from .ParameterCollector import ParameterCollector


__all__ = [
    "ParameterCollector",
]


_DESIGN_NOTES = """
# core/parameter_collector

## Contents
An internal helper class for collecting and ordering `inspect.Parameter`
instances during signature construction.

| Name                 | Description                                                      |
|----------------------|------------------------------------------------------------------|
| `ParameterCollector` | Stores and manages parameters grouped by kind — core logic for signature assembly |
"""
