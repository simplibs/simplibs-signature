"""
Tests for signature_copy decorator — copying and transforming signatures.
Supports Iterable types for 'extras' and 'excepts' and ensures decorator stability.
"""
import pytest
import inspect
import asyncio
from typing import Optional, Iterable

# Ensure pytest-asyncio is installed for async decorator tests
pytest.importorskip("pytest_asyncio", reason="pytest-asyncio is required for async decorator tests")

# Imports based on the provided project structure
from src.simplibs.signature.decorators.signature_copy import signature_copy
from src.simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

def source_func(a: int, b: str = "default") -> float:
    """The base function to copy from."""
    return 1.0


async def async_source(x: int) -> str:
    """An async source function."""
    await asyncio.sleep(0)
    return str(x)


# -----------------------------------------------------------------------------
# Basic Copying & Transformation
# -----------------------------------------------------------------------------

def test_signature_copy_basic():
    """Should copy the signature from a source function to a target function."""

    @signature_copy(source_func)
    def target(*args, **kwargs):
        return source_func(*args, **kwargs)

    sig = inspect.signature(target)
    assert list(sig.parameters.keys()) == ["a", "b"]
    assert sig.return_annotation is float
    assert target(10, "hello") == 1.0


@pytest.mark.parametrize("collection_type", [list, tuple, set])
def test_signature_copy_with_modifications_iterables(collection_type):
    """Should allow renaming return type and excluding parameters using various iterables."""
    excludes = collection_type(["b"])

    @signature_copy(source_func, returns=int, excepts=excludes)
    def target(a):
        return int(source_func(a))

    sig = inspect.signature(target)
    assert list(sig.parameters.keys()) == ["a"]
    assert "b" not in sig.parameters
    assert sig.return_annotation is int


# -----------------------------------------------------------------------------
# Async Support
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signature_copy_async_to_async():
    """Should correctly copy a signature between async functions."""

    @signature_copy(async_source)
    async def wrapped_async(x):
        return await async_source(x)

    sig = inspect.signature(wrapped_async)
    assert "x" in sig.parameters
    assert inspect.iscoroutinefunction(wrapped_async)

    result = await wrapped_async(42)
    assert result == "42"


@pytest.mark.asyncio
async def test_signature_copy_sync_to_async():
    """Should allow copying a sync signature onto an async function."""

    @signature_copy(source_func)
    async def target_async(*args, **kwargs):
        return source_func(*args, **kwargs)

    sig = inspect.signature(target_async)
    assert list(sig.parameters.keys()) == ["a", "b"]
    assert inspect.iscoroutinefunction(target_async)


# -----------------------------------------------------------------------------
# Advanced Features (Extras & Bindings)
# -----------------------------------------------------------------------------

def test_signature_copy_with_extras_as_generator():
    """Should allow adding extra parameters provided as a generator (testing sanitization)."""
    def extra_gen():
        yield inspect.Parameter("c", inspect.Parameter.KEYWORD_ONLY, default=True)

    # Decorator factory should consume the generator and keep the data stable
    copy_decorator = signature_copy(source_func, extras=extra_gen())

    @copy_decorator
    def target_1(a, b, c=True): pass

    @copy_decorator
    def target_2(a, b, c=True): pass

    # Verify both targets have the same stable signature
    for target in (target_1, target_2):
        sig = inspect.signature(target)
        assert "c" in sig.parameters
        assert sig.parameters["c"].kind == inspect.Parameter.KEYWORD_ONLY


def test_signature_copy_excludes_binding():
    """Should support excluding 'self' or 'cls' via the include_binding flag."""

    class MyClass:
        def method(self, x: int): pass

    @signature_copy(MyClass.method, include_binding=False)
    def external_func(x): pass

    sig = inspect.signature(external_func)
    assert "self" not in sig.parameters
    assert "x" in sig.parameters


# -----------------------------------------------------------------------------
# Validation & Error Handling
# -----------------------------------------------------------------------------

def test_signature_copy_raises_on_invalid_base_func():
    """Should raise SignatureParameterError if base_func is not callable."""
    with pytest.raises(SignatureParameterError):
        signature_copy("not-a-callable")  # type: ignore


def test_signature_copy_raises_on_invalid_extras_string_trap():
    """Should raise SignatureParameterError if extras is a raw string (String Trap)."""
    with pytest.raises(SignatureParameterError):
        signature_copy(source_func, extras="not-an-iterable")  # type: ignore


def test_signature_copy_respects_validate_false():
    """Should bypass initial validation if validate=False."""
    # This skips the top-level type checks
    try:
        signature_copy(source_func, extras="invalid", validate=False) # type: ignore
    except (TypeError, ValueError, SignatureBuildError):
        pass


# -----------------------------------------------------------------------------
# Flat Mode Integration
# -----------------------------------------------------------------------------

def test_signature_copy_flat_mode_integration():
    """
    Verify that flat_to_kwargs converts all copied parameters to KEYWORD_ONLY
    when applied as a decorator.
    """
    def local_source(a, b=1): pass

    @signature_copy(local_source, flat_to_kwargs=True)
    def decorated_func(*args, **kwargs):
        pass

    sig = inspect.signature(decorated_func)
    assert len(sig.parameters) == 2
    for param in sig.parameters.values():
        assert param.kind == inspect.Parameter.KEYWORD_ONLY


def test_signature_copy_raises_on_invalid_flat_to_kwargs_type():
    """Should raise SignatureParameterError if flat_to_kwargs is not a boolean."""
    with pytest.raises(SignatureParameterError):
        signature_copy(source_func, flat_to_kwargs="not-a-bool")  # type: ignore