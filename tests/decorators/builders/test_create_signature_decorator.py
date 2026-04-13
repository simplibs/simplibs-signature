"""
Tests for create_signature_decorator — factory for creating signature-applying decorators.
"""
import pytest
import inspect
import asyncio
from typing import Callable

# Ensure pytest-asyncio is installed for async tests
pytest.importorskip("pytest_asyncio", reason="pytest-asyncio is required for async decorator tests")

# Imports based on the provided project structure
from src.simplibs.signature.decorators.builders.create_signature_decorator import create_signature_decorator
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

@pytest.fixture
def sample_signature():
    """A basic signature for testing the decorator."""
    params = [
        inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
        inspect.Parameter("y", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    ]
    return inspect.Signature(params, return_annotation=int)


# -----------------------------------------------------------------------------
# Decorator Functionality
# -----------------------------------------------------------------------------

def test_decorator_application_sync(sample_signature):
    """Should create a decorator that correctly applies a signature to a sync function."""
    decorator = create_signature_decorator(sample_signature)

    @decorator
    def my_func(a, b):
        return a + b

    # Verify the signature was injected
    sig = inspect.signature(my_func)
    assert sig == sample_signature
    assert list(sig.parameters.keys()) == ["x", "y"]

    # Verify execution is still correct
    assert my_func(5, 5) == 10


@pytest.mark.asyncio
async def test_decorator_application_async(sample_signature):
    """Should create a decorator that correctly applies a signature to an async function."""
    decorator = create_signature_decorator(sample_signature)

    @decorator
    async def my_async_func(a, b):
        await asyncio.sleep(0)
        return a * b

    # Verify the signature was injected
    sig = inspect.signature(my_async_func)
    assert sig == sample_signature

    # Verify it's still a coroutine function
    assert inspect.iscoroutinefunction(my_async_func)

    # Verify execution (must be awaited)
    result = await my_async_func(2, 4)
    assert result == 8


def test_decorator_reusability(sample_signature):
    """Should allow using the same decorator on multiple functions."""
    apply_sig = create_signature_decorator(sample_signature)

    @apply_sig
    def func_one(a, b): pass

    @apply_sig
    def func_two(c, d): pass

    assert inspect.signature(func_one) == sample_signature
    assert inspect.signature(func_two) == sample_signature


# -----------------------------------------------------------------------------
# Validation & Error Handling
# -----------------------------------------------------------------------------

def test_factory_raises_on_invalid_signature():
    """Should raise SignatureParameterError immediately if signature is invalid (Early Validation)."""
    with pytest.raises(SignatureParameterError):
        # Passing a string instead of inspect.Signature object
        create_signature_decorator("not-a-signature")  # type: ignore


def test_decorator_raises_on_invalid_decoration_target(sample_signature):
    """Should raise SignatureParameterError when applying the decorator to a non-callable."""
    decorator = create_signature_decorator(sample_signature)

    with pytest.raises(SignatureParameterError):
        # Trying to decorate a string instead of a function
        decorator("not-a-function")  # type: ignore


def test_factory_respects_validate_false():
    """Should skip early validation when validate=False is passed to the factory."""
    # This should not raise an error during factory creation
    decorator = create_signature_decorator("invalid-sig", validate=False)  # type: ignore
    assert callable(decorator)