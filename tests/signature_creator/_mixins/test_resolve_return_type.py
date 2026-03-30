"""
Tests for ResolveReturnTypeMixin — finalisation of _return_type for inspect.Signature.
"""
import inspect
import pytest
from simplibs.signature.signature_creator.SignatureCreator import SignatureCreator


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def func_returns_float(x) -> float: ...
def func_returns_list(x) -> list: ...
def func_no_annotation(x): ...


# -----------------------------------------------------------------------------
# Type — passed through unchanged
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("return_type", [int, str, float, list, dict])
def test_type_is_passed_through(return_type):
    """A type passed as return_type must appear unchanged as the return annotation."""
    sc = SignatureCreator(func_no_annotation, return_type=return_type)
    assert sc.signature.return_annotation is return_type


def test_custom_class_is_passed_through():
    """A custom class passed as return_type must appear unchanged as the return annotation."""
    class MyClass: ...
    sc = SignatureCreator(func_no_annotation, return_type=MyClass)
    assert sc.signature.return_annotation is MyClass


# -----------------------------------------------------------------------------
# None — passed through (removes annotation)
# -----------------------------------------------------------------------------

def test_none_return_type_yields_none():
    """return_type=None must result in None as the return annotation (explicit -> None)."""
    sc = SignatureCreator(func_returns_float, return_type=None)
    assert sc.signature.return_annotation is None

# -----------------------------------------------------------------------------
# Callable — replaced with its return annotation
# -----------------------------------------------------------------------------

def test_callable_return_type_is_resolved():
    """A callable passed as return_type must be replaced with its return annotation."""
    sc = SignatureCreator(func_no_annotation, return_type=func_returns_float)
    assert sc.signature.return_annotation is float


def test_callable_return_type_overrides_base_func():
    """A callable passed as return_type must override base_func's own annotation."""
    sc = SignatureCreator(base_func=func_returns_float, return_type=func_returns_list)
    assert sc.signature.return_annotation is list


def test_callable_without_annotation_yields_empty():
    """A callable with no return annotation passed as return_type must yield inspect.Signature.empty."""
    sc = SignatureCreator(func_no_annotation, return_type=func_no_annotation)
    assert sc.signature.return_annotation is inspect.Signature.empty


# -----------------------------------------------------------------------------
# UNSET — becomes inspect.Signature.empty
# -----------------------------------------------------------------------------

def test_unset_with_no_base_func_annotation_yields_empty():
    """When return_type is omitted and base_func has no annotation, result must be inspect.Signature.empty."""
    sc = SignatureCreator(base_func=func_no_annotation)
    assert sc.signature.return_annotation is inspect.Signature.empty


def test_unset_with_base_func_annotation_inherits_it():
    """When return_type is omitted and base_func has an annotation, it must be inherited."""
    sc = SignatureCreator(base_func=func_returns_float)
    assert sc.signature.return_annotation is float