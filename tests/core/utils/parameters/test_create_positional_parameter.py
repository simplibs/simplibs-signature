"""
Tests for create_positional_parameter — factory for positional inspect.Parameter instances.
"""
import pytest
import inspect
from typing import Any

# Imports based on the provided project structure
from src.simplibs.signature.core.utils.parameters.create_positional_parameter import create_positional_parameter
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid Parameter Creation
# -----------------------------------------------------------------------------

def test_create_standard_positional_parameter():
    """Should create a POSITIONAL_OR_KEYWORD parameter by default."""
    param = create_positional_parameter("x")

    assert isinstance(param, inspect.Parameter)
    assert param.name == "x"
    assert param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert param.default is inspect.Parameter.empty
    assert param.annotation is inspect.Parameter.empty


def test_create_positional_only_parameter():
    """Should create a POSITIONAL_ONLY parameter when requested."""
    param = create_positional_parameter("y", positional_only=True)

    assert param.name == "y"
    assert param.kind == inspect.Parameter.POSITIONAL_ONLY


def test_create_with_default_and_annotation():
    """Should correctly assign default value and type annotation."""
    param = create_positional_parameter(
        "z",
        default=42,
        annotation=int
    )

    assert param.name == "z"
    assert param.default == 42
    assert param.annotation is int


# -----------------------------------------------------------------------------
# Validation & Errors
# -----------------------------------------------------------------------------

def test_invalid_name_type_raises():
    """Should raise SignatureParameterError if name is not a string."""
    with pytest.raises(SignatureParameterError) as exc_info:
        create_positional_parameter(123)  # type: ignore

    assert isinstance(exc_info.value, TypeError)
    assert "name" in str(exc_info.value.value_label)


def test_mismatched_default_and_annotation_raises():
    """Should raise SignatureParameterError if default does not match simple annotation."""
    with pytest.raises(SignatureParameterError) as exc_info:
        create_positional_parameter("x", default="not_an_int", annotation=int)

    assert isinstance(exc_info.value, TypeError)
    assert "default" in str(exc_info.value.value_label)


def test_skip_validation():
    """
    Should skip custom validations when validate=False.
    Note: We test this using default/annotation mismatch because Python's
    inspect.Parameter ALWAYS enforces that name must be a string.
    """
    # This would normally raise SignatureParameterError due to type mismatch,
    # but validate=False allows it to pass to inspect.Parameter, which doesn't care.
    param = create_positional_parameter(
        name="valid_name",
        default="string_value",
        annotation=int,
        validate=False
    )

    assert param.name == "valid_name"
    assert param.default == "string_value"
    assert param.annotation is int


# -----------------------------------------------------------------------------
# Edge Cases
# -----------------------------------------------------------------------------

def test_none_as_default_passes():
    """None as default should pass even if annotation is provided."""
    param = create_positional_parameter("x", default=None, annotation=int)
    assert param.default is None


def test_complex_annotation_is_ignored_by_validation():
    """Complex annotations (like list[int]) should not trigger validation errors for defaults."""
    param = create_positional_parameter("items", default=42, annotation=list[int])
    assert param.default == 42