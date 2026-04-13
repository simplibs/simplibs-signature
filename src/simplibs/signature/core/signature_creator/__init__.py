from .SignatureCreator import SignatureCreator


__all__ = [
    "SignatureCreator",
]


_DESIGN_NOTES = """
# core/signature_creator

## Contents
The orchestrator class for building complex `inspect.Signature` objects
from multiple sources (parameters, callables).

| Name                 | Description                                                      |
|----------------------|------------------------------------------------------------------|
| `SignatureCreator`   | Builder class — assembles signatures from mixed sources          |
"""
