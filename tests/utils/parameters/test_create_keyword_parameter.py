"""
Tests for create_keyword_parameter — return type, parameter kind, name, annotation, default, and validation.
"""
import inspect
import pytest
from simplibs.signature.utils.parameters.create_keyword_parameter import create_keyword_parameter
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Return type and kind
# -----------------------------------------------------------------------------

def test_returns_inspect_parameter():
    """Must return an inspect.Parameter instance."""
    assert isinstance(create_keyword_parameter("x"), inspect.Parameter)


def test_kind_is_keyword_only():
    """The returned parameter must be KEYWORD_ONLY."""
    assert create_keyword_parameter("x").kind == inspect.Parameter.KEYWORD_ONLY


# -----------------------------------------------------------------------------
# Name
# -----------------------------------------------------------------------------

def test_name_is_set_correctly():
    """The parameter name must match the provided name."""
    assert create_keyword_parameter("timeout").name == "timeout"


# -----------------------------------------------------------------------------
# Annotation
# -----------------------------------------------------------------------------

def test_annotation_is_set_when_provided():
    """The annotation must match the provided type."""
    assert create_keyword_parameter("x", annotation=int).annotation == int


def test_annotation_is_empty_when_not_provided():
    """The annotation must be inspect.Parameter.empty when not provided."""
    assert create_keyword_parameter("x").annotation == inspect.Parameter.empty


# -----------------------------------------------------------------------------
# Default
# -----------------------------------------------------------------------------

def test_default_is_set_when_provided():
    """The default must match the provided value."""
    assert create_keyword_parameter("x", default=30).default == 30


def test_default_is_empty_when_not_provided():
    """The default must be inspect.Parameter.empty when not provided."""
    assert create_keyword_parameter("x").default == inspect.Parameter.empty


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

def test_invalid_name_raises():
    """A non-string name must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        create_keyword_parameter(42)


def test_invalid_annotation_raises():
    """A non-type annotation must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        create_keyword_parameter("x", annotation="int")


def test_validate_false_skips_validation():
    """validate=False must skip our validation — invalid annotation passes through."""
    param = create_keyword_parameter("x", annotation="int", validate=False)
    assert param.annotation == "int"