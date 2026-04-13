"""
Tests for @signature_set — assigning pre-constructed signatures to functions.
"""
import pytest
import inspect
import asyncio

# Ensure pytest-asyncio is installed for async decorator tests
pytest.importorskip("pytest_asyncio", reason="pytest-asyncio is required for async decorator tests")

# Imports based on the provided project structure
from src.simplibs.signature.decorators.signature_set import signature_set
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

@pytest.fixture
def simple_sig():
    """A pre-constructed signature: (x: int, y: str = 'default') -> bool"""
    params = [
        inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
        inspect.Parameter("y", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str, default="default"),
    ]
    return inspect.Signature(params, return_annotation=bool)


# -----------------------------------------------------------------------------
# Basic Assignment
# -----------------------------------------------------------------------------

def test_signature_set_assigns_correctly(simple_sig):
    """Should strictly assign the provided signature to a target function."""

    @signature_set(simple_sig)
    def my_func(*args, **kwargs):
        return True

    sig = inspect.signature(my_func)
    assert sig == simple_sig
    assert list(sig.parameters.keys()) == ["x", "y"]
    assert sig.return_annotation is bool
    # Test execution
    assert my_func(10, y="hello") is True


def test_signature_set_works_as_shared_constant(simple_sig):
    """Should allow using the same signature instance for multiple functions."""

    @signature_set(simple_sig)
    def func_a(x, y): pass

    @signature_set(simple_sig)
    def func_b(x, y): pass

    assert inspect.signature(func_a) == inspect.signature(func_b) == simple_sig


# -----------------------------------------------------------------------------
# Async Support
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signature_set_on_async_function(simple_sig):
    """Should correctly apply a signature to an async function and preserve awaitability."""

    @signature_set(simple_sig)
    async def my_async_func(x, y):
        await asyncio.sleep(0)
        return True

    # Check signature
    assert inspect.signature(my_async_func) == simple_sig

    # Check async nature
    assert inspect.iscoroutinefunction(my_async_func)

    # Check execution
    result = await my_async_func(1, "test")
    assert result is True


# -----------------------------------------------------------------------------
# Validation & Error Handling
# -----------------------------------------------------------------------------

def test_signature_set_raises_on_invalid_input():
    """Should raise SignatureParameterError if the input is not an inspect.Signature."""

    # Case 1: Passing a function instead of a signature
    with pytest.raises(SignatureParameterError):
        signature_set(lambda x: x)  # type: ignore

    # Case 2: Passing a string
    with pytest.raises(SignatureParameterError):
        signature_set("not-a-signature")  # type: ignore


def test_signature_set_decorator_validates_target_callable(simple_sig):
    """The returned decorator should raise an error if applied to a non-callable."""
    decorator = signature_set(simple_sig)

    with pytest.raises(SignatureParameterError):
        decorator("not-a-callable")  # type: ignore