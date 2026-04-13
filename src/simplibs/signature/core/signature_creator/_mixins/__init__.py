from .ProcessParamSources import ProcessParamSourcesMixin
from .ProcessReturnSource import ProcessReturnSourceMixin


__all__ = [
    "ProcessParamSourcesMixin",
    "ProcessReturnSourceMixin",
]


_DESIGN_NOTES = """
# core/signature_creator/_mixins

## Contents
Mixins for `SignatureCreator` — each handles one aspect of signature assembly.

| Name                        | Method                    | Description                                      |
|-----------------------------|---------------------------|--------------------------------------------------|
| `ProcessParamSourcesMixin`  | `_process_param_sources()`| Iterate over parameter sources and collect them |
| `ProcessReturnSourceMixin`  | `_process_return_source()`| Resolve and finalize the return annotation     |
"""
