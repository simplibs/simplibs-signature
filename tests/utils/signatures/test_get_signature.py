"""
Tests for get_signature — return type, valid callables, validation, and failure modes.
"""
import inspect
import pytest
from simplibs.signature.utils.signatures.get_signature import get_signature
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError
from simplibs.signature.utils._validations.exceptions.SignatureBuildError import SignatureBuildError


# -----------------------------------------------------------------------------
# Return type
# -----------------------------------------------------------------------------

def test_returns_inspect_signature():
    """Must return an inspect.Signature instance."""
    def my_func(x: int, y: str): ...
    assert isinstance(get_signature(my_func), inspect.Signature)


# -----------------------------------------------------------------------------
# Valid callables
# -----------------------------------------------------------------------------

def test_regular_function_passes():
    """A regular function must return its signature."""
    def my_func(a, b, c=1): ...
    sig = get_signature(my_func)
    assert list(sig.parameters.keys()) == ["a", "b", "c"]


def test_lambda_passes():
    """A lambda must return its signature."""
    sig = get_signature(lambda x, y: x + y)
    assert list(sig.parameters.keys()) == ["x", "y"]


def test_class_init_passes():
    """A class __init__ must return its signature."""
    class MyClass:
        def __init__(self, name: str, value: int = 0): ...
    sig = get_signature(MyClass.__init__)
    assert "name" in sig.parameters


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

def test_non_callable_raises_signature_parameter_error():
    """A non-callable must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        get_signature(42)


def test_validate_false_skips_validation():
    """validate=False must skip the callable check."""
    def my_func(): ...
    sig = get_signature(my_func, validate=False)
    assert isinstance(sig, inspect.Signature)


# -----------------------------------------------------------------------------
# Failure modes
# -----------------------------------------------------------------------------

def test_builtin_without_signature_raises_signature_build_error():
    """A built-in without introspectable signature must raise SignatureBuildError."""
    with pytest.raises(SignatureBuildError):
        get_signature(object.__subclasshook__)