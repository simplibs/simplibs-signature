from .constants import BINDING_NAMES, VARIADIC_NAMES, ARGS, KWARGS
from .parameter_collector import ParameterCollector
from .signature_creator import SignatureCreator
from .utils import (
    create_positional_parameter,
    create_keyword_parameter,
    get_signature,
    set_signature,
    compose_signature,
    add_params_to_signature,
    delete_params_from_signature,
    replace_return_annotation_in_signature,
)
from .validators import (
    # validate_is_bool,
    # validate_is_callable,
    # validate_is_string,
    # validate_default_matches_annotation,
    # validate_parameters_collection,
    # validate_is_inspect_signature,
    # validate_excluded_names,
    # validate_param_sources,
    SignatureError,
    SignatureBuildError,
    SignatureParameterError,
)


__all__ = [
    # Constants
    "BINDING_NAMES",
    "VARIADIC_NAMES",
    "ARGS",
    "KWARGS",
    # Classes
    "ParameterCollector",
    "SignatureCreator",
    # Parameter utilities
    "create_positional_parameter",
    "create_keyword_parameter",
    # Signature operations
    "get_signature",
    "set_signature",
    "compose_signature",
    # Signature modifiers
    "add_params_to_signature",
    "delete_params_from_signature",
    "replace_return_annotation_in_signature",
    # Validators
    # "validate_is_bool",
    # "validate_is_callable",
    # "validate_is_string",
    # "validate_default_matches_annotation",
    # "validate_parameters_collection",
    # "validate_is_inspect_signature",
    # "validate_excluded_names",
    # "validate_param_sources",
    # Exceptions
    "SignatureError",
    "SignatureBuildError",
    "SignatureParameterError",
]


_DESIGN_NOTES = """
# core

## Contents
Core implementation module — validators, builders, utilities, and exceptions.
Most of this is internal; users typically import from the top-level `simplibs.signature`.

## Submodules

### constants
Pre-built parameters and sentinel sets.

### parameter_collector
Internal parameter grouping and ordering engine.

### signature_creator
Builder class and mixin logic for assembling signatures.

### utils
User-facing utilities (parameter factories, operations, modifiers).

### validators
Validation functions and exception classes.
"""
