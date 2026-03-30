"""
Tests for create_signature_decorator — decorator factory, signature application, and validation delegation.
"""
import inspect
import pytest
from simplibs.signature.signature_decorators.utils.create_signature_decorator import create_signature_decorator
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def sample_func(x: int) -> float:
    return 1.0


@pytest.fixture
def custom_signature():
    param = inspect.Parameter("z", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    return inspect.Signature([param], return_annotation=bool)


# -----------------------------------------------------------------------------
# Factory return value
# -----------------------------------------------------------------------------

def test_returns_callable(custom_signature):
    """create_signature_decorator must return a callable (the decorator)."""
    decorator = create_signature_decorator(custom_signature)
    assert callable(decorator)


# -----------------------------------------------------------------------------
# Decorator application
# -----------------------------------------------------------------------------

def test_decorator_returns_callable(custom_signature):
    """The decorator must return a callable when applied to a function."""
    decorator = create_signature_decorator(custom_signature)
    wrapper = decorator(sample_func)
    assert callable(wrapper)


def test_wrapper_has_assigned_signature(custom_signature):
    """The wrapper must have the assigned signature accessible via __signature__."""
    decorator = create_signature_decorator(custom_signature)
    wrapper = decorator(sample_func)
    assert wrapper.__signature__ is custom_signature


def test_inspect_signature_returns_assigned(custom_signature):
    """inspect.signature() on the wrapper must return the assigned signature."""
    decorator = create_signature_decorator(custom_signature)
    wrapper = decorator(sample_func)
    assert inspect.signature(wrapper) == custom_signature


def test_decorator_syntax_works(custom_signature):
    """The factory must work correctly when used with @ decorator syntax."""
    decorator = create_signature_decorator(custom_signature)

    @decorator
    def my_func(*args, **kwargs):
        return 42

    assert inspect.signature(my_func) == custom_signature
    assert my_func() == 42


# -----------------------------------------------------------------------------
# Call forwarding
# -----------------------------------------------------------------------------

def test_wrapper_forwards_call(custom_signature):
    """The wrapper must forward calls to the original function."""
    def add(a, b):
        return a + b

    sig = inspect.Signature([
        inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD),
        inspect.Parameter("b", inspect.Parameter.POSITIONAL_OR_KEYWORD),
    ])
    wrapper = create_signature_decorator(sig)(add)
    assert wrapper(2, 3) == 5


# -----------------------------------------------------------------------------
# Validation timing — factory vs decoration
# -----------------------------------------------------------------------------

def test_invalid_signature_does_not_raise_at_factory_time():
    """An invalid signature must NOT raise when the decorator is created — only when applied."""
    decorator = create_signature_decorator("not_a_signature")
    assert callable(decorator)


def test_invalid_signature_raises_at_decoration_time():
    """An invalid signature must raise SignatureParameterError when the decorator is applied."""
    decorator = create_signature_decorator("not_a_signature")
    with pytest.raises(SignatureParameterError) as exc_info:
        decorator(sample_func)
    assert isinstance(exc_info.value, TypeError)


# -----------------------------------------------------------------------------
# validate=False
# -----------------------------------------------------------------------------

def test_validate_false_skips_validation_at_decoration_time():
    """validate=False must skip validation even when an invalid signature is provided."""
    decorator = create_signature_decorator("not_a_signature", validate=False)
    result = decorator(sample_func)
    assert callable(result)