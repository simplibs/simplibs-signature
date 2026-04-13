"""
Tests for set_signature — assigning inspect.Signature to callables via __signature__.
"""
import pytest
import inspect
from typing import Callable

# Imports based on the provided project structure
from src.simplibs.signature.core.utils.operations.set_signature import set_signature
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

@pytest.fixture
def empty_signature():
    """Provides a minimal valid inspect.Signature."""
    return inspect.Signature()


def sample_function(a, b):
    return a + b


class SampleClass:
    def __call__(self, x):
        return x


# -----------------------------------------------------------------------------
# Valid Signature Assignment
# -----------------------------------------------------------------------------

def test_set_signature_on_function(empty_signature):
    """Should assign signature to a standard function and return it."""
    original_sig = inspect.signature(sample_function)
    assert original_sig != empty_signature

    returned_func = set_signature(sample_function, empty_signature)

    assert returned_func is sample_function
    assert sample_function.__signature__ == empty_signature
    assert inspect.signature(sample_function) == empty_signature


def test_set_signature_on_lambda(empty_signature):
    """Should work correctly with lambda functions."""
    my_lambda = lambda x: x
    set_signature(my_lambda, empty_signature)

    assert my_lambda.__signature__ == empty_signature


def test_set_signature_on_callable_instance(empty_signature):
    """Should work on instances of classes that implement __call__."""
    obj = SampleClass()
    set_signature(obj, empty_signature)

    assert obj.__signature__ == empty_signature


# -----------------------------------------------------------------------------
# Validation & Errors
# -----------------------------------------------------------------------------

def test_set_signature_invalid_function_raises(empty_signature):
    """Should raise SignatureParameterError if the first argument is not callable."""
    with pytest.raises(SignatureParameterError) as exc_info:
        set_signature("not_a_function", empty_signature)

    assert isinstance(exc_info.value, TypeError)
    assert "function" in str(exc_info.value.value_label)


def test_set_signature_invalid_signature_raises():
    """Should raise SignatureParameterError if the second argument is not a Signature object."""
    with pytest.raises(SignatureParameterError) as exc_info:
        set_signature(sample_function, "not_a_signature")  # type: ignore

    assert isinstance(exc_info.value, TypeError)
    assert "signature" in str(exc_info.value.value_label)


def test_set_signature_skip_validation():
    """
    Should skip validations when validate=False.
    We test this by passing an invalid signature type (string).
    Python allows setting almost anything to __signature__, so this should pass.
    """
    fake_signature = "I am a string, not a Signature"

    # This would raise SignatureParameterError if validate=True
    returned_func = set_signature(
        sample_function,
        fake_signature,  # type: ignore
        validate=False
    )

    assert returned_func.__signature__ == fake_signature


# -----------------------------------------------------------------------------
# Cleanup (to avoid side effects in other tests)
# -----------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def cleanup_signature():
    """Ensures sample_function is reset after each test."""
    yield
    if hasattr(sample_function, "__signature__"):
        del sample_function.__signature__