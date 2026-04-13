"""
Tests for @signature — the universal master decorator for signature manipulation.
Supports Iterable types for the 'excepts' parameter and ensures late-binding stability.
"""
import pytest
import inspect
import asyncio
from typing import Callable, Iterable

# Ensure pytest-asyncio is installed for async decorator tests
pytest.importorskip("pytest_asyncio", reason="pytest-asyncio is required for async decorator tests")

# Imports based on the provided project structure
from src.simplibs.signature.decorators.signature import signature
from src.simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

def base_func(a: int, b: int) -> int:
    """A simple base function."""
    return a + b


async def async_base(x: int) -> str:
    """An async base function."""
    await asyncio.sleep(0)
    return str(x)


# -----------------------------------------------------------------------------
# Basic Composition (Merging)
# -----------------------------------------------------------------------------

def test_signature_merge_with_decorated_func():
    """Should merge provided parameters with the decorated function's signature."""
    extra_param = inspect.Parameter("c", inspect.Parameter.KEYWORD_ONLY, default=10)

    @signature(extra_param)  # use_func=True and func_first=True by default
    def target(a: int, b: int):
        return a + b

    sig = inspect.signature(target)
    assert list(sig.parameters.keys()) == ["a", "b", "c"]
    assert sig.parameters["c"].default == 10


def test_signature_override_with_use_func_false():
    """Should completely ignore the decorated function's signature if use_func=False."""
    new_param = inspect.Parameter("only_me", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    @signature(new_param, use_func=False, returns=str)
    def target(*args, **kwargs):
        return "result"

    sig = inspect.signature(target)
    assert list(sig.parameters.keys()) == ["only_me"]
    assert sig.return_annotation is str


# -----------------------------------------------------------------------------
# Async Support & Late Binding
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_signature_on_async_function():
    """Should correctly wrap an async function and preserve its coroutine nature."""
    extra = inspect.Parameter("debug", inspect.Parameter.KEYWORD_ONLY, default=False)

    @signature(extra)
    async def my_async_task(data: dict):
        await asyncio.sleep(0)
        return True

    # Check signature
    sig = inspect.signature(my_async_task)
    assert "data" in sig.parameters
    assert "debug" in sig.parameters

    # Check async nature
    assert inspect.iscoroutinefunction(my_async_task)

    # Check execution
    result = await my_async_task({"id": 1})
    assert result is True


# -----------------------------------------------------------------------------
# Advanced Ordering (func_first)
# -----------------------------------------------------------------------------

def test_signature_ordering_func_first_false():
    """Should place decorated function's parameters AFTER provided params when func_first=False."""
    prefix_param = inspect.Parameter("prefix", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    @signature(prefix_param, func_first=False)
    def target(a, b):
        pass

    sig = inspect.signature(target)
    # Expected: (prefix, a, b) because params are foundation, function is added after
    assert list(sig.parameters.keys()) == ["prefix", "a", "b"]


# -----------------------------------------------------------------------------
# Filtering (excepts with Iterable support)
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("collection_type", [list, tuple, set])
def test_signature_filtering_with_iterables(collection_type):
    """Should allow removing parameters using various iterable types for 'excepts'."""
    excludes = collection_type(["b"])

    @signature(excepts=excludes, include_variadic=False)
    def target(a, b, *args):
        pass

    sig = inspect.signature(target)
    assert "a" in sig.parameters
    assert "b" not in sig.parameters
    assert "args" not in sig.parameters


def test_signature_filtering_with_generator():
    """Should correctly handle a generator in 'excepts' (testing sanitization)."""
    gen_excludes = (name for name in ["b"])

    @signature(excepts=gen_excludes)
    def target(a, b):
        pass

    sig = inspect.signature(target)
    assert "a" in sig.parameters
    assert "b" not in sig.parameters


# -----------------------------------------------------------------------------
# Validation & Errors
# -----------------------------------------------------------------------------

def test_signature_raises_on_invalid_usage_string_trap():
    """Should raise SignatureParameterError if 'excepts' is a raw string (String Trap)."""
    with pytest.raises(SignatureParameterError):
        @signature(excepts="b")  # type: ignore
        def target(a, b): pass


def test_signature_raises_on_invalid_parameter_sequence():
    """
    Should raise SignatureBuildError if parameters are provided in an invalid order
    (non-default after default), as the library enforces strict Python syntax.
    """
    param_with_default = inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=1)
    param_no_default = inspect.Parameter("b", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    # We expect a SignatureBuildError because 'b' follows 'a=1'
    with pytest.raises(SignatureBuildError) as exc_info:
        @signature(param_with_default, param_no_default, use_func=False)
        def target(*args):
            pass

    # Verify that the error message mentions the invalid order
    assert "INVALID PARAMETER ORDER" in str(exc_info.value)
    assert "cannot follow parameters that already have default values" in str(exc_info.value)


def test_signature_respects_validate_false():
    """Should bypass validation at decoration time if validate=False."""
    # This should not raise SignatureParameterError during decoration
    @signature(excepts="not-an-iterable", validate=False) # type: ignore
    def target(a): pass

    # Note: It might still fail during signature assembly, but the entry-point validation is skipped.


# -----------------------------------------------------------------------------
# Flat Mode Integration
# -----------------------------------------------------------------------------

def test_signature_decorator_flat_mode_integration():
    """
    Verify that flat_to_kwargs converts all parameters (from decorated function
    and extra params) to KEYWORD_ONLY when applied as a master decorator.
    """
    extra_p = inspect.Parameter("extra", inspect.Parameter.POSITIONAL_ONLY)

    @signature(extra_p, flat_to_kwargs=True)
    def target_func(a, b=1):
        pass

    sig = inspect.signature(target_func)

    # We expect 3 parameters: a, b (from function) and extra (from decorator)
    assert len(sig.parameters) == 3
    for name in ["a", "b", "extra"]:
        assert sig.parameters[name].kind == inspect.Parameter.KEYWORD_ONLY


def test_signature_decorator_raises_on_invalid_flat_to_kwargs_type():
    """Should raise SignatureParameterError if flat_to_kwargs is not a boolean."""
    with pytest.raises(SignatureParameterError):
        @signature(flat_to_kwargs="not-a-bool")  # type: ignore
        def target(): pass