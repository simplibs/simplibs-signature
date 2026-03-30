from .ProcessFunc import ProcessFuncMixin
from .ProcessSources import ProcessSourcesMixin
from .ProcessParameters import ProcessParametersMixin
from .ResolveReturnType import ResolveReturnTypeMixin


_DESIGN_NOTES = """
# signature_creator/_mixins

## Contents
Mixins for `SignatureCreator` — each provides one step of the signature
assembly pipeline.

| Name                      | Method                   | Description                                                    |
|---------------------------|--------------------------|----------------------------------------------------------------|
| `ProcessFuncMixin`        | `_process_func()`        | Extracts parameters and optionally resolves return type from a callable |
| `ProcessSourcesMixin`     | `_process_sources()`     | Iterates over sources and routes each item to the correct handler |
| `ProcessParametersMixin`  | `_process_parameters()`  | Orchestrates processing order based on `base_func_first`       |
| `ResolveReturnTypeMixin`  | `_resolve_return_type()` | Finalises `_return_type` into a form `inspect.Signature` accepts |
"""