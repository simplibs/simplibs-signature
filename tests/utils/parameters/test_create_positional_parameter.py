"""
Tests for create_positional_parameter — return type, parameter kind, name, annotation, default, and validation.
"""
import inspect
import pytest
from simplibs.signature.utils.parameters.create_positional_parameter import create_positional_parameter
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Return type
# -----------------------------------------------------------------------------

def test_returns_inspect_parameter():
    """Must return an inspect.Parameter instance."""
    assert isinstance(create_positional_parameter("x"), inspect.Parameter)


# -----------------------------------------------------------------------------
# Parameter kind
# -----------------------------------------------------------------------------

def test_default_kind_is_positional_or_keyword():
    """Default kind must be POSITIONAL_OR_KEYWORD."""
    assert create_positional_parameter("x").kind == inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_positional_only_true_produces_positional_only():
    """positional_only=True must produce a POSITIONAL_ONLY parameter."""
    assert create_positional_parameter("x", positional_only=True).kind == inspect.Parameter.POSITIONAL_ONLY


def test_positional_only_false_produces_positional_or_keyword():
    """positional_only=False must produce a POSITIONAL_OR_KEYWORD parameter."""
    assert create_positional_parameter("x", positional_only=False).kind == inspect.Parameter.POSITIONAL_OR_KEYWORD


# -----------------------------------------------------------------------------
# Name
# -----------------------------------------------------------------------------

def test_name_is_set_correctly():
    """The parameter name must match the provided name."""
    assert create_positional_parameter("count").name == "count"


# -----------------------------------------------------------------------------
# Annotation
# -----------------------------------------------------------------------------

def test_annotation_is_set_when_provided():
    """The annotation must match the provided type."""
    assert create_positional_parameter("x", annotation=int).annotation == int


def test_annotation_is_empty_when_not_provided():
    """The annotation must be inspect.Parameter.empty when not provided."""
    assert create_positional_parameter("x").annotation == inspect.Parameter.empty


# -----------------------------------------------------------------------------
# Default
# -----------------------------------------------------------------------------

def test_default_is_set_when_provided():
    """The default must match the provided value."""
    assert create_positional_parameter("x", default=0).default == 0


def test_default_is_empty_when_not_provided():
    """The default must be inspect.Parameter.empty when not provided."""
    assert create_positional_parameter("x").default == inspect.Parameter.empty


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

def test_invalid_name_raises():
    """A non-string name must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        create_positional_parameter(42)


def test_invalid_annotation_raises():
    """A non-type annotation must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        create_positional_parameter("x", annotation="int")


def test_validate_false_skips_validation():
    """validate=False must skip our validation — invalid annotation passes through."""
    param = create_positional_parameter("x", annotation="int", validate=False)
    assert param.annotation == "int"