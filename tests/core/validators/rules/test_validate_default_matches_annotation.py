"""
Tests for validate_default_matches_annotation — type matching, edge cases, and error fields.
"""
import pytest
import inspect
from typing import Any, Union, Optional

from simplibs.signature.core.validators._rules.validate_default_matches_annotation import (
    validate_default_matches_annotation,
)
from simplibs.signature.core.validators.exceptions import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid values — matching types
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value, annotation", [
    (42, int),
    ("hello", str),
    ([1, 2, 3], list),
])
def test_basic_types_match_pass(value, annotation):
    """Basic types matching their annotations must pass."""
    validate_default_matches_annotation(value, annotation)


def test_custom_class_and_subclass_pass():
    """Instances of matching classes or subclasses must pass."""
    class Parent: pass
    class Child(Parent): pass

    validate_default_matches_annotation(Parent(), Parent)
    validate_default_matches_annotation(Child(), Parent)


# -----------------------------------------------------------------------------
# Skipped validation — no validation should occur
# -----------------------------------------------------------------------------

def test_none_default_skips_validation():
    """None as default must skip validation (permissive approach)."""
    validate_default_matches_annotation(None, int)


def test_empty_default_skips_validation():
    """inspect.Parameter.empty as default must skip validation."""
    validate_default_matches_annotation(inspect.Parameter.empty, int)


def test_empty_annotation_skips_validation():
    """inspect.Parameter.empty as annotation must skip validation."""
    validate_default_matches_annotation(42, inspect.Parameter.empty)


def test_complex_annotations_skip_validation():
    """Union, Any, and Optional are not concrete types and must be skipped."""
    validate_default_matches_annotation(42, Union[int, str])
    validate_default_matches_annotation("anything", Any)
    validate_default_matches_annotation(42, Optional[int])


# -----------------------------------------------------------------------------
# Invalid values — type mismatch
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("value, annotation", [
    ("hello", int),
    (42, str),
    ([1, 2], dict),
])
def test_type_mismatch_raises(value, annotation):
    """Obvious type mismatches must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        validate_default_matches_annotation(value, annotation)


# -----------------------------------------------------------------------------
# Error fields
# -----------------------------------------------------------------------------

def test_error_fields_are_correct():
    """The raised exception must have correctly populated fields and useful message."""
    with pytest.raises(SignatureParameterError) as exc_info:
        validate_default_matches_annotation("not_an_int", int)

    e = exc_info.value
    assert e.value == "not_an_int"
    assert e.value_label == "default for parameter"
    assert e.error_name == "INVALID DEFAULT VALUE"
    assert "int" in str(e.expected).lower()
    assert isinstance(e, TypeError)