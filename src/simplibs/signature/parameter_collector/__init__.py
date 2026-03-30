from .ParameterCollector import ParameterCollector


_DESIGN_NOTES = """
# parameter_collector

## Contents
An internal helper class for collecting and ordering `inspect.Parameter`
instances during signature construction.

| Name                 | Description                                                          |
|----------------------|----------------------------------------------------------------------|
| `ParameterCollector` | Stores and manages parameters grouped by kind — used by `SignatureCreator` |
"""