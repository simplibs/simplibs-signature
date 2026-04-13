from .SignatureError import SignatureError
from .SignatureBuildError import SignatureBuildError
from .SignatureParameterError import SignatureParameterError


__all__ = [
    "SignatureError",
    "SignatureBuildError",
    "SignatureParameterError",
]


_DESIGN_NOTES = """
# core/validators/exceptions

## Contents
Structured exception classes for signature-related errors.

| Name                        | Parent Class        | Description                              |
|-----------------------------|---------------------|------------------------------------------|
| `SignatureError`            | SimpleException     | Base — catches all signature errors     |
| `SignatureBuildError`       | SignatureError      | Signature assembly/structure failed     |
| `SignatureParameterError`   | SignatureError      | Invalid argument type passed by user    |
"""
