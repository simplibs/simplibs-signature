from .builders import apply_signature_to_wraps, create_signature_decorator
from .signature import signature
from .signature_copy import signature_copy
from .signature_set import signature_set


_DESIGN_NOTES = """
# Signature Decorators Sub-Package

## Purpose
Decorators that give a function the signature it should report. Plain imports,
no `__all__`: the package root decides what is public.

## Internal Components Registry

| Component         | Type        | Description                                              |
| :---------------- | :---------- | :------------------------------------------------------ |
| `signature`       | Decorator   | Assembles a signature from several sources.              |
| `signature_copy`  | Decorator   | Copies another callable's signature, with changes.       |
| `signature_set`   | Decorator   | Attaches a finished signature.                           |
| `builders`        | Sub-package | `apply_signature_to_wraps` and `create_signature_decorator`. |
"""
