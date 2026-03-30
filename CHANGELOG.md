# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

## [0.1.0] - 2026-03-30

### Added
- **Core Decorators** — `signature_copy` for copying/normalizing signatures 
  and `signature_from` for assembling signatures from multiple sources.
- **Signature Creation Engine** — `SignatureCreator` (builder class)
  and `create_signature` (functional interface) for declarative signature assembly.
- **Signature Operations** — `get_signature` with structured error handling, 
  `set_signature` for easy `__signature__` assignment, and `create_copy_signature` 
  for low-level control.
- **Parameter Factories** — `create_positional_parameter` and `create_keyword_parameter` 
  for building `inspect.Parameter` objects without boilerplate.
- **Parameter Management** — `ParameterCollector` class for internal grouping 
  and ordering of parameters by kind.
- **Decorator Utilities** — `apply_signature_to_wraps` and `create_signature_decorator` 
  for building custom signature-aware decorators.
- **Constants** — Pre-defined `ARGS` (`*args`), `KWARGS` (`**kwargs`), 
  and `EXCLUDED` (defaulting to `self`, `cls`).
- **Structured Exceptions** — Integrated with the Simple ecosystem; 
  provides `SignatureError`, `SignatureBuildError`, and `SignatureParameterError`.
- **Validation Suite** — Robust internal validation for types, 
  callables, and signature compatibility.
- Full test coverage (~273 tests)