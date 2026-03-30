"""
Tests for ProcessFuncMixin — parameter extraction, return type resolution, and is_base_func logic.
"""
import inspect
import pytest
from simplibs.sentinels import UNSET
from simplibs.signature.signature_creator.SignatureCreator import SignatureCreator


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def func_a(x: int, y: str) -> float: ...
def func_b(z: bool) -> list: ...
def func_no_return(a): ...


# -----------------------------------------------------------------------------
# Parameter extraction
# -----------------------------------------------------------------------------

def test_parameters_from_base_func_are_extracted():
    """Parameters from base_func must appear in the signature."""
    sc = SignatureCreator(base_func=func_a)
    assert "x" in sc.signature.parameters
    assert "y" in sc.signature.parameters


def test_parameters_from_sources_callable_are_extracted():
    """Parameters from a callable in sources must appear in the signature."""
    sc = SignatureCreator(func_b)
    assert "z" in sc.signature.parameters


def test_all_parameters_are_extracted():
    """All parameters from the callable must be present, none missing."""
    sc = SignatureCreator(base_func=func_a)
    assert list(sc.signature.parameters.keys()) == ["x", "y"]


# -----------------------------------------------------------------------------
# Return type — base_func inheritance
# -----------------------------------------------------------------------------

def test_return_type_inherited_from_base_func_when_unset():
    """Return annotation must be inherited from base_func when return_type is UNSET."""
    sc = SignatureCreator(base_func=func_a)
    assert sc.signature.return_annotation is float


def test_return_type_not_inherited_from_sources_callable_when_unset():
    """Return annotation must NOT be inherited from a callable in sources when return_type is UNSET."""
    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    sc = SignatureCreator(func_b, base_func=func_no_return)
    assert sc.signature.return_annotation is not list


def test_explicit_return_type_not_overwritten_by_base_func():
    """An explicitly passed return_type must not be overwritten by base_func's annotation."""
    sc = SignatureCreator(base_func=func_a, return_type=int)
    assert sc.signature.return_annotation is int


# -----------------------------------------------------------------------------
# Return type — callable as return_type
# -----------------------------------------------------------------------------

def test_return_type_extracted_from_callable_passed_as_return_type():
    """When a callable is passed as return_type, its return annotation must be used."""
    sc = SignatureCreator(base_func=func_no_return, return_type=func_a)
    assert sc.signature.return_annotation is float


def test_return_type_from_callable_overrides_base_func_annotation():
    """A callable passed as return_type must take precedence over base_func's annotation."""
    sc = SignatureCreator(base_func=func_a, return_type=func_b)
    assert sc.signature.return_annotation is list


# -----------------------------------------------------------------------------
# No return annotation
# -----------------------------------------------------------------------------

def test_no_return_annotation_results_in_empty():
    """A function without a return annotation must yield inspect.Signature.empty."""
    sc = SignatureCreator(base_func=func_no_return)
    assert sc.signature.return_annotation is inspect.Signature.empty