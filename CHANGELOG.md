# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.3.0] - 2026-11-07

A rewrite of the internals to the current simplibs style. The everyday API is the same
(`@signature`, `@signature_copy`, `create_signature`, `copy_signature`, the modifiers and
the parameter creators), but some names changed and the exceptions are different, so please
read the **Breaking** section before upgrading.

### ⚠️ Breaking

* **Exceptions**:
  The library no longer defines its own exceptions (`SignatureError`, `SignatureBuildError`,
  `SignatureParameterError` are gone). Every error is now a `ParamError` card from
  `simplibs-exception`. Where a card wraps a standard exception, that type is in its MRO,
  so `except ValueError`, `except TypeError` and `except SyntaxError` keep working.
* **`validate` → `_validate_call`**:
  The `validate` switch is replaced by the reserved `_validate_call` of `@validate_call`
  from `simplibs-validate`. `False` skips the validation of the arguments of that call.
  Argument validation itself is now done by `@validate_call` on every public function.
* **Removed classes and helpers**:
  `SignatureCreator` and its mixins, `validate_signature_params()` and
  `validate_is_inspect_signature()` no longer exist. `create_signature` is a plain function
  built on `ParameterCollector`.
* **Constants**:
  `BINDING_NAMES` is now an internal `frozenset` and is no longer exported; `VARIADIC_NAMES`
  is removed (see *Changed*, `include_variadic`).
* **`include_variadic=False` now works by kind**:
  It leaves out every `*args` and `**kwargs` whatever they are called (`*a`, `**options`),
  where it used to match only the names `args` and `kwargs`.

### ✨ Added

* **`ParameterCollector` is public**:
  Exported from the package root, with `add_param`, `add_params` and `get_ordered_params`.
* **One slot per variadic kind**:
  A second `*args` (or `**kwargs`) under another name is a collision and is settled by
  `accept_double` / `replace_double`. Before, `(*a, *b)` could be built, because `inspect`
  accepts it.
* **Collision messages for variadics**:
  `DUPLICATE PARAMETER ERROR` names the stored variadic it collides with.
* **Documentation**:
  A new main README and four detailed READMEs in `docs/` (decorators, orchestrators,
  parameter collector, tools), with a look "under the hood" for every function.

### 🔄 Changed

* **Package structure**:
  Reorganised into `collector`, `constants`, `decorators`, `orchestrators` and `tools`
  (`parameters`, `operations`, `modifiers`). Only the root `__init__` defines `__all__`;
  the sub-packages use plain imports. Each layer imports only from the layers before it.
* **`compose_signature` always validates the structure**:
  It no longer passes the undocumented `__validate_parameters__=False` to `inspect`.
  `_validate_call` controls only `@validate_call`. A duplicate name can no longer be merged
  silently.
* **Iterables are read once**:
  `compose_signature` and `add_params_to_signature` turn their input into a tuple first, so
  an error card shows the parameters that failed instead of an exhausted generator.
* **Any iterable, also a generator**:
  Every public function with an `Iterable[...]` parameter (`excepts`, `extras`, `excluded_names`,
  `extra_params`, `params_to_add`, `parameters`) uses `@validate_call(materialize_iterators=True)`: a list, a
  tuple, a set or a generator works, and a generator is read once and arrives as a tuple. Variadic parameters
  are annotated naturally (`*params: inspect.Parameter | Callable`).
* **Flat mode**:
  `replace_double=False` keeps both colliding parameters and renames the later one
  (`name_1`, `name_2`, ...). This is now documented on every public function.
* **`raise_invalid_parameter_order_error`**:
  Uses the same `label` (`param.name`) as the duplicate error.

### 🐛 Fixed

* **Stale name index after a replacement**:
  The collector forgets the name of a replaced parameter, so a later real parameter with
  that name is no longer taken for a duplicate.
* **Misleading messages**:
  `raise_invalid_parameter_source_error` now suggests `create_signature(*my_list)`;
  `raise_signature_structure_value_error` no longer advises on a "second `*args`".

### 📋 Improved

* **Design notes and docstrings**:
  Every module, including every `__init__`, has `_DESIGN_NOTES` with its purpose and, for
  the packages, a table of its components. All public functions have complete docstrings.
* **Tests**:
  Rewritten in a structure that mirrors the sources (about 380 tests). Errors are tested
  with `assert_exception_function` from `simplibs-exception`.
* **Dependencies**:
  Now builds on `simplibs-exception`, `simplibs-validate` and `simplibs-sentinels`. It needs
  `simplibs-validate>=0.4.1` (natural `*args` annotations, `materialize_iterators` and parameters whose
  default is `inspect.Parameter.empty`).

---

## [0.2.3] - 2026-09-07

### 🐛 Fixed

* **Root Exception `skip_locations` Field**:  
  Renamed `_skip_locations` to `skip_locations` in `SignatureError` to align with 
  the constructor contract of `simplibs-exception`. This ensures internal library 
  stack frames are correctly filtered out from tracebacks, pointing diagnostics 
  directly to user code.
* **Migration to `simplibs-exception` v1.0+**:  
  Renamed all deprecated `value_label` parameters/attributes across internal exception 
  construction sites to `label` to conform with the updated `simplibs-exception` 1.0+ API.

### 📋 Improved

* **Core Dependency Update**:  
  Upgraded `simplibs-exception` to `>=1.0.2` across project metadata to ensure 
  full compatibility with modern exception reporting and typed context managers.

---

## [0.2.2] - 2026-04-13

### Changed
- **Documentation** — Updated README to reflect decorator rename: `signature_from` → `@signature`
  - Clarifies the public API and improves documentation accuracy
  - No functional changes to the library

---

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
