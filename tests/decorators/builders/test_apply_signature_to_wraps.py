"""
Tests for apply_signature_to_wraps — creating signature-aware wrappers for sync and async functions.
"""
import pytest
import inspect
import asyncio
from typing import Callable

# Ensure pytest-asyncio is installed, otherwise skip these tests with a clear message
pytest.importorskip("pytest_asyncio", reason="pytest-asyncio is required to run async wrapper tests")

# Imports based on the provided project structure
from src.simplibs.signature.decorators.builders.apply_signature_to_wraps import apply_signature_to_wraps
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

def sync_function(a: int, b: int) -> int:
    """A simple synchronous function."""
    return a + b

async def async_function(x: int, y: int) -> int:
    """A simple asynchronous function."""
    await asyncio.sleep(0)
    return x * y

@pytest.fixture
def custom_signature():
    """A custom signature to be applied."""
    params = [
        inspect.Parameter("custom_param", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str)
    ]
    return inspect.Signature(params, return_annotation=bool)


# -----------------------------------------------------------------------------
# Synchronous Wrapping
# -----------------------------------------------------------------------------

def test_apply_to_sync_function(custom_signature):
    """Should wrap a sync function and apply the custom signature."""
    wrapper = apply_signature_to_wraps(sync_function, custom_signature)

    # Check if it's still a sync function (not a coroutine function)
    assert not inspect.iscoroutinefunction(wrapper)

    # Check signature injection
    sig = inspect.signature(wrapper)
    assert sig == custom_signature
    assert "custom_param" in sig.parameters

    # Check execution (transparency)
    assert wrapper(10, 20) == 30


def test_metadata_preservation_sync(custom_signature):
    """Should preserve docstrings and names via @wraps for sync functions."""
    wrapper = apply_signature_to_wraps(sync_function, custom_signature)

    assert wrapper.__name__ == "sync_function"
    assert wrapper.__doc__ == "A simple synchronous function."


# -----------------------------------------------------------------------------
# Asynchronous Wrapping
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_apply_to_async_function(custom_signature):
    """Should wrap an async function and apply the custom signature."""
    wrapper = apply_signature_to_wraps(async_function, custom_signature)

    # Check if it's correctly identified as an async function
    assert inspect.iscoroutinefunction(wrapper)

    # Check signature injection
    sig = inspect.signature(wrapper)
    assert sig == custom_signature

    # Check execution (must be awaited)
    result = await wrapper(2, 5)
    assert result == 10


@pytest.mark.asyncio
async def test_metadata_preservation_async(custom_signature):
    """Should preserve docstrings and names via @wraps for async functions."""
    wrapper = apply_signature_to_wraps(async_function, custom_signature)

    assert wrapper.__name__ == "async_function"
    assert "A simple asynchronous function" in wrapper.__doc__


# -----------------------------------------------------------------------------
# Validation & Error Handling
# -----------------------------------------------------------------------------

def test_apply_raises_on_invalid_function(custom_signature):
    """Should raise SignatureParameterError if the function is not callable."""
    with pytest.raises(SignatureParameterError):
        apply_signature_to_wraps("not-a-callable", custom_signature) # type: ignore


def test_apply_raises_on_invalid_signature():
    """Should raise SignatureParameterError if the signature is not an inspect.Signature."""
    with pytest.raises(SignatureParameterError):
        apply_signature_to_wraps(sync_function, "not-a-signature") # type: ignore