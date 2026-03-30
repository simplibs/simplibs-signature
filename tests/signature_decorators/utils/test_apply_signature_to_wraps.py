"""
Tests for apply_signature_to_wraps — wrapper creation, signature assignment, metadata, and validation.
"""
import inspect
import pytest
from simplibs.signature.signature_decorators.utils.apply_signature_to_wraps import apply_signature_to_wraps
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def sample_func(x: int, y: str) -> float:
    """Sample docstring."""
    return 1.0


@pytest.fixture
def custom_signature():
    param = inspect.Parameter("z", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    return inspect.Signature([param], return_annotation=bool)


# -----------------------------------------------------------------------------
# Return value
# -----------------------------------------------------------------------------

def test_returns_callable(custom_signature):
    """apply_signature_to_wraps must return a callable."""
    wrapper = apply_signature_to_wraps(sample_func, custom_signature)
    assert callable(wrapper)


# -----------------------------------------------------------------------------
# Signature assignment
# -----------------------------------------------------------------------------

def test_wrapper_has_assigned_signature(custom_signature):
    """The wrapper's __signature__ must be the assigned signature."""
    wrapper = apply_signature_to_wraps(sample_func, custom_signature)
    assert wrapper.__signature__ is custom_signature


def test_inspect_signature_returns_assigned(custom_signature):
    """inspect.signature() on the wrapper must return the assigned signature."""
    wrapper = apply_signature_to_wraps(sample_func, custom_signature)
    assert inspect.signature(wrapper) == custom_signature


# -----------------------------------------------------------------------------
# Metadata preservation
# -----------------------------------------------------------------------------

def test_wrapper_preserves_name(custom_signature):
    """The wrapper must preserve the original function's __name__."""
    wrapper = apply_signature_to_wraps(sample_func, custom_signature)
    assert wrapper.__name__ == sample_func.__name__


def test_wrapper_preserves_doc(custom_signature):
    """The wrapper must preserve the original function's __doc__."""
    wrapper = apply_signature_to_wraps(sample_func, custom_signature)
    assert wrapper.__doc__ == sample_func.__doc__


def test_wrapper_preserves_module(custom_signature):
    """The wrapper must preserve the original function's __module__."""
    wrapper = apply_signature_to_wraps(sample_func, custom_signature)
    assert wrapper.__module__ == sample_func.__module__


# -----------------------------------------------------------------------------
# Call forwarding
# -----------------------------------------------------------------------------

def test_wrapper_forwards_call(custom_signature):
    """The wrapper must forward calls to the original function and return its result."""
    def add(a, b):
        return a + b
    sig = inspect.Signature([
        inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD),
        inspect.Parameter("b", inspect.Parameter.POSITIONAL_OR_KEYWORD),
    ])
    wrapper = apply_signature_to_wraps(add, sig)
    assert wrapper(1, 2) == 3


# -----------------------------------------------------------------------------
# validate=False
# -----------------------------------------------------------------------------

def test_validate_false_skips_validation():
    """validate=False must skip validation and not raise even for invalid inputs."""
    apply_signature_to_wraps("not_a_callable", "not_a_signature", validate=False)


# -----------------------------------------------------------------------------
# Validation errors
# -----------------------------------------------------------------------------

def test_invalid_function_raises(custom_signature):
    """A non-callable function must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        apply_signature_to_wraps(42, custom_signature)
    assert isinstance(exc_info.value, TypeError)


def test_invalid_signature_raises():
    """A non-Signature signature must raise SignatureParameterError."""
    with pytest.raises(SignatureParameterError) as exc_info:
        apply_signature_to_wraps(sample_func, "not_a_signature")
    assert isinstance(exc_info.value, TypeError)


def test_function_validated_before_signature():
    """function must be validated before signature — invalid function raises first."""
    with pytest.raises(SignatureParameterError) as exc_info:
        apply_signature_to_wraps(42, "not_a_signature")
    assert exc_info.value.value_label == "function"