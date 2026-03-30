"""
Tests for set_signature — return value, signature assignment, validation, and chaining.
"""
import inspect
import pytest
from simplibs.signature.utils.signatures.set_signature import set_signature
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Return value
# -----------------------------------------------------------------------------

def test_returns_original_function():
    """Must return the original function — allows inline assignment."""
    def my_func(): ...
    sig = inspect.Signature()
    assert set_signature(my_func, sig) is my_func


# -----------------------------------------------------------------------------
# Signature assignment
# -----------------------------------------------------------------------------

def test_signature_is_assigned():
    """The signature must be assigned to __signature__."""
    def my_func(x: int): ...
    new_sig = inspect.Signature([
        inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ])
    set_signature(my_func, new_sig)
    assert inspect.signature(my_func) == new_sig


def test_empty_signature_is_assigned():
    """An empty signature must be assignable."""
    def my_func(x: int): ...
    empty_sig = inspect.Signature()
    set_signature(my_func, empty_sig)
    assert inspect.signature(my_func) == empty_sig


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

def test_non_callable_raises():
    """A non-callable function argument must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        set_signature(42, inspect.Signature())


def test_non_signature_raises():
    """A non-Signature signature argument must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError):
        def my_func(): ...
        set_signature(my_func, "not_a_signature")


def test_validate_false_skips_validation():
    """validate=False must skip all checks — function is modified directly."""
    def my_func(): ...
    sig = inspect.Signature()
    set_signature(my_func, sig, validate=False)
    assert inspect.signature(my_func) == sig