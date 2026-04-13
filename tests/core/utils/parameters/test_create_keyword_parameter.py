"""
Tests for create_keyword_parameter — factory for KEYWORD_ONLY inspect.Parameter instances.
"""
import pytest
import inspect
from typing import Any

# Imports based on the provided project structure
from src.simplibs.signature.core.utils.parameters.create_keyword_parameter import create_keyword_parameter
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Valid Parameter Creation
# -----------------------------------------------------------------------------

def test_create_standard_keyword_parameter():
    """Should create a KEYWORD_ONLY parameter with default empty values."""
    param = create_keyword_parameter("k")

    assert isinstance(param, inspect.Parameter)
    assert param.name == "k"
    assert param.kind == inspect.Parameter.KEYWORD_ONLY
    assert param.default is inspect.Parameter.empty
    assert param.annotation is inspect.Parameter.empty


def test_create_with_full_metadata():
    """Should correctly assign name, default value, and type annotation."""
    param = create_keyword_parameter(
        "api_key",
        default="secret",
        annotation=str
    )

    assert param.name == "api_key"
    assert param.kind == inspect.Parameter.KEYWORD_ONLY
    assert param.default == "secret"
    assert param.annotation is str


# -----------------------------------------------------------------------------
# Validation & Errors
# -----------------------------------------------------------------------------

def test_invalid_name_type_raises():
    """Should raise SignatureParameterError if name is not a string (when validate=True)."""
    with pytest.raises(SignatureParameterError) as exc_info:
        create_keyword_parameter(None)  # type: ignore

    assert isinstance(exc_info.value, TypeError)
    assert "name" in str(exc_info.value.value_label)


def test_mismatched_default_and_annotation_raises():
    """Should raise SignatureParameterError if default type does not match annotation."""
    with pytest.raises(SignatureParameterError) as exc_info:
        create_keyword_parameter("count", default="not_an_int", annotation=int)

    assert isinstance(exc_info.value, TypeError)
    assert "default" in str(exc_info.value.value_label)


def test_skip_validation():
    """
    Should skip custom validations when validate=False.
    Using type mismatch to bypass library validation while keeping Python's inspect happy.
    """
    # Custom validator would catch this, but validate=False lets it through to inspect
    param = create_keyword_parameter(
        name="any_name",
        default=123,
        annotation=str,
        validate=False
    )

    assert param.name == "any_name"
    assert param.default == 123
    assert param.annotation is str


# -----------------------------------------------------------------------------
# Edge Cases
# -----------------------------------------------------------------------------

def test_none_as_default_is_allowed():
    """None as default should be accepted even with specific type annotation."""
    param = create_keyword_parameter("callback", default=None, annotation=str)
    assert param.default is None


def test_complex_annotation_handling():
    """Should allow complex annotations that the simple validator ignores."""
    # Simple validator skips checks if it doesn't recognize the annotation as a simple type
    param = create_keyword_parameter("data", default={"id": 1}, annotation=dict[str, int])
    assert param.default == {"id": 1}
    assert param.annotation == dict[str, int]