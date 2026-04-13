"""
Tests for get_signature — safe wrapper for inspect.signature().
"""
import pytest
import inspect
import sys
from typing import Callable

# Imports based on the provided project structure
from src.simplibs.signature.core.utils.operations.get_signature import get_signature
from src.simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

def sample_func(x: int, y: str = "default") -> bool:
    return True

class CallableClass:
    def __call__(self, arg1):
        pass


# -----------------------------------------------------------------------------
# Valid Signature Retrieval
# -----------------------------------------------------------------------------

def test_get_signature_from_standard_function():
    """Should return a valid inspect.Signature from a standard function."""
    sig = get_signature(sample_func)

    assert isinstance(sig, inspect.Signature)
    assert "x" in sig.parameters
    assert sig.return_annotation is bool


def test_get_signature_from_callable_instance():
    """Should return a valid signature from a class instance with __call__."""
    obj = CallableClass()
    sig = get_signature(obj)
    assert isinstance(sig, inspect.Signature)
    assert "arg1" in sig.parameters


# -----------------------------------------------------------------------------
# Error Handling & Introspection Failures
# -----------------------------------------------------------------------------

def test_get_signature_non_callable_raises():
    """Should raise SignatureParameterError if input is not callable (when validate=True)."""
    with pytest.raises(SignatureParameterError) as exc_info:
        get_signature("I am not a function") # type: ignore

    assert isinstance(exc_info.value, TypeError)
    assert "function" in str(exc_info.value.value_label)


def test_get_signature_introspection_value_error():
    """
    Should raise SignatureBuildError wrapped around ValueError.
    Triggered by objects that are callable but don't provide signature metadata.
    """
    # Many built-ins (like sys.getsizeof or int) raise ValueError: "no signature found"
    with pytest.raises(SignatureBuildError) as exc_info:
        get_signature(sys.getsizeof)

    assert exc_info.value.error_name == "SIGNATURE INTROSPECTION ERROR"
    # We check for ValueError (the cause of the fail)
    assert isinstance(exc_info.value.__cause__, ValueError)


def test_get_signature_introspection_type_error():
    """
    Should raise SignatureBuildError wrapped around TypeError.
    Triggered by objects that inspect.signature() refuses to even try to process.
    """
    with pytest.raises(SignatureBuildError) as exc_info:
        # Passing None with validate=False forces inspect.signature to raise TypeError
        # because it requires a callable, and None is never considered one.
        get_signature(None, validate=False) # type: ignore

    assert exc_info.value.error_name == "SIGNATURE INTROSPECTION ERROR"
    # In Python 3.11+, inspect.signature(None) raises TypeError
    assert isinstance(exc_info.value.__cause__, TypeError)


# -----------------------------------------------------------------------------
# Validation Bypass
# -----------------------------------------------------------------------------

def test_get_signature_skip_validation():
    """Should skip the initial validate_is_callable check when validate=False."""
    # When validation is skipped, the error is caught by the internal try-except block
    with pytest.raises(SignatureBuildError) as exc_info:
        get_signature("string", validate=False) # type: ignore

    assert exc_info.value.error_name == "SIGNATURE INTROSPECTION ERROR"
    assert "context" in exc_info.value.__dict__