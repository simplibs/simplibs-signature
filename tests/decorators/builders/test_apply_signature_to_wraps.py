import asyncio
import inspect

import pytest

from simplibs.signature import apply_signature_to_wraps

P = inspect.Parameter


def _signature():
    return inspect.Signature([P("only", P.KEYWORD_ONLY)], return_annotation=int)


def test_the_wrapper_reports_the_given_signature():
    def function(a, b):
        return a + b

    wrapper = apply_signature_to_wraps(function, _signature())

    assert inspect.signature(wrapper) == _signature()


def test_calls_are_forwarded_unchanged():
    def function(a, b=2, *, c=3):
        return (a, b, c)

    wrapper = apply_signature_to_wraps(function, _signature())

    assert wrapper(1, c=9) == (1, 2, 9)


def test_returns_a_new_function_and_leaves_the_original_alone():
    def function(a):
        return a

    wrapper = apply_signature_to_wraps(function, _signature())

    assert wrapper is not function
    assert not hasattr(function, "__signature__")
    assert str(inspect.signature(function)) == "(a)"


def test_keeps_the_metadata():
    def function(a):
        """The docstring."""

    wrapper = apply_signature_to_wraps(function, _signature())

    assert wrapper.__name__ == "function"
    assert wrapper.__doc__ == "The docstring."
    assert wrapper.__wrapped__ is function


def test_exceptions_pass_through():
    def function():
        raise KeyError("boom")

    with pytest.raises(KeyError):
        apply_signature_to_wraps(function, _signature())()


def test_a_plain_function_gets_a_plain_wrapper():
    wrapper = apply_signature_to_wraps(lambda: 1, _signature())

    assert not inspect.iscoroutinefunction(wrapper)


def test_a_coroutine_function_gets_an_async_wrapper():
    async def function(a):
        return a * 2

    wrapper = apply_signature_to_wraps(function, _signature())

    assert inspect.iscoroutinefunction(wrapper)
    assert asyncio.run(wrapper(21)) == 42


def test_an_async_wrapper_passes_exceptions_through():
    async def function():
        raise KeyError("boom")

    wrapper = apply_signature_to_wraps(function, _signature())

    with pytest.raises(KeyError):
        asyncio.run(wrapper())


def test_validation_switch_is_accepted():
    wrapper = apply_signature_to_wraps(lambda: 1, _signature(), _validate_call=False)

    assert wrapper() == 1
