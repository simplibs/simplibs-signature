"""
Tests for ParameterCollector — initialisation, excluded names, accept_double, param_list structure, and validation.
"""
import inspect
import pytest
from simplibs.signature.parameter_collector.ParameterCollector import ParameterCollector
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def make_param(name: str, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD) -> inspect.Parameter:
    return inspect.Parameter(name, kind)


# -----------------------------------------------------------------------------
# Default initialisation
# -----------------------------------------------------------------------------

def test_default_excluded_names_contains_self_and_cls():
    """Default _excluded_names must contain 'self' and 'cls'."""
    collector = ParameterCollector()
    assert "self" in collector._excluded_names
    assert "cls" in collector._excluded_names


def test_default_accept_double_is_true():
    """Default _accept_double must be True."""
    assert ParameterCollector()._accept_double is True


def test_param_list_has_all_five_kinds():
    """_param_list must contain all five inspect.Parameter kinds."""
    collector = ParameterCollector()
    expected_kinds = {
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.VAR_POSITIONAL,
        inspect.Parameter.KEYWORD_ONLY,
        inspect.Parameter.VAR_KEYWORD,
    }
    assert set(collector._param_list.keys()) == expected_kinds


def test_param_list_starts_empty():
    """All lists in _param_list must be empty on initialisation."""
    collector = ParameterCollector()
    assert all(lst == [] for lst in collector._param_list.values())


def test_seen_names_starts_empty():
    """_seen_names must be empty on initialisation."""
    assert ParameterCollector()._seen_names == set()


# -----------------------------------------------------------------------------
# Custom excluded_names
# -----------------------------------------------------------------------------

def test_custom_excluded_names_extend_defaults():
    """Custom excluded_names must be added on top of the default EXCLUDED set."""
    collector = ParameterCollector(excluded_names=("my_param",))
    assert "self" in collector._excluded_names
    assert "cls" in collector._excluded_names
    assert "my_param" in collector._excluded_names


def test_none_excluded_names_uses_defaults_only():
    """excluded_names=None must result in only the default exclusions."""
    collector = ParameterCollector(excluded_names=None)
    assert collector._excluded_names == {"self", "cls"}


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

def test_invalid_excluded_names_raises():
    """A non-tuple excluded_names must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        ParameterCollector(excluded_names=["self"])


def test_invalid_accept_double_raises():
    """A non-bool accept_double must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        ParameterCollector(accept_double=1)