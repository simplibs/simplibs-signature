# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).


## [0.2.1] - 2026-04-13

### Fixed
- Updated dependency `simplibs-exception>=0.2.0` in `pyproject.toml`
  (was requiring outdated 0.1.0)

---

## [0.2.0] - 2026-04-08

### Added
- **Flat Mode Integration** — New `flat_to_kwargs` parameter added across all builders (`create_signature`, `copy_signature`) and decorators (`@signature`, `@signature_copy`). This allows for one-click transformation of all parameters into `KEYWORD_ONLY` kind.
- **Functional Builders** — `create_signature()` and `copy_signature()` as primary 
  entry points for signature creation, with intelligent dispatch between simple 
  and complex assembly paths.
- **Enhanced Configuration** — `replace_double`, `include_variadic`, and `include_binding` 
  flags for fine-grained control over deduplication and parameter filtering.
- **Signature Modifiers** — `add_params_to_signature()`, `delete_params_from_signature()`, 
  and `replace_return_annotation_in_signature()` for surgical signature transformation.
- **Simplified Decorator API** — Redesigned `@signature` and `@signature_copy` decorators 
  with cleaner parameter names (`returns`, `extras`, `excepts`, `use_func`, `func_first`).
- **Decorator Builders** — Low-level utilities `apply_signature_to_wraps()` and 
  `create_signature_decorator()` exposed for advanced custom decorator patterns.
- **Constants Proliferation** — Exported `BINDING_NAMES` and `VARIADIC_NAMES` 
  as sources of truth for filtering logic.
- **Exception Transparency** — All exceptions now included in `__all__` export 
  for explicit exception handling in user code.
- **Comprehensive Validation** — Validators `validate_signature_params()` and 
  `validate_is_inspect_signature()` available for reuse in custom workflows.

### Changed
- **Flexible Iterable Inputs** — All functions and decorators that previously required `tuple` for parameters or names (like `extras`, `excepts`, `excluded_names`) now accept any **`Iterable`** (lists, sets, or generators). Inputs are internally sanitized and stabilized.
- **Architecture Refactor** — Removed `base_func` and `base_func_first` parameters 
  from `SignatureCreator.__init__()`; decorator layer now handles source ordering 
  via parameter composition.
- **Decorator Parameter Naming** — Shortened names for decorator use: 
  `return_annotation` → `returns`, `extra_params` → `extras`, 
  `excluded_names` → `excepts`.
- **Module Reorganization** — Flattened imports; core operations now more accessible 
  directly from `simplibs.signature` root.
- **Validation Pipeline** — Streamlined internal validation; `validate=False` now 
  consistently skips redundant checks in trusted pipeline contexts.
- **Default Behavior** — Parameter filtering now opt-in via `include_variadic` 
  and `include_binding`; explicit control instead of convention.

### Fixed
- **Async Detection Robustness** — Improved handling of edge-case async callables 
  in decorator wrapping.
- **Error Context Precision** — All validation errors now include precise file:line 
  references via `get_location=2`.
- **Return Annotation Handling** — Fixed edge case where `None` was conflated with 
  "no return annotation"; now properly distinguished via `UNSET` sentinel.

### Removed
- `create_copy_signature()` — Functionality merged into `copy_signature()` 
  (lower-level interface still available via composition).
- Parameter normalization flags from `SignatureCreator` — Now decorator's concern.

### Internal
- **ParameterCollector Evolution** — Core logic refined with improved indexing strategy 
  for O(1) duplicate detection and support for on-the-fly keyword-only transformation.
- Full redesign of `_DESIGN_NOTES` documentation across all modules 
  (comprehensive maintenance guide for future developers).
- Mixin-based architecture solidified for `SignatureCreator` 
  (`ProcessParamSourcesMixin`, `ProcessReturnSourceMixin`).

---

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
- **Structured Exceptions** — Integrated with the simplibs ecosystem; 
  provides `SignatureError`, `SignatureBuildError`, and `SignatureParameterError`.
- **Validation Suite** — Robust internal validation for types, 
  callables, and signature compatibility.
- Full test coverage (~273 tests)
