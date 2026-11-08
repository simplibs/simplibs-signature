import asyncio
import inspect

from simplibs.signature import signature_set

P = inspect.Parameter


def _signature():
    return inspect.Signature([P("only", P.KEYWORD_ONLY)], return_annotation=int)


def test_attaches_the_given_signature():
    @signature_set(_signature())
    def function(a, b):
        ...

    assert inspect.signature(function) == _signature()


def test_the_original_function_is_not_modified():
    def function(a, b):
        ...

    signature_set(_signature())(function)

    assert str(inspect.signature(function)) == "(a, b)"
    assert not hasattr(function, "__signature__")


def test_the_wrapper_still_works():
    @signature_set(_signature())
    def function(a, b):
        return a + b

    assert function(1, 2) == 3


def test_one_decorator_serves_many_functions():
    decorator = signature_set(_signature())

    first, second = decorator(lambda: 1), decorator(lambda: 2)

    assert inspect.signature(first) == inspect.signature(second) == _signature()


def test_a_coroutine_function_stays_awaitable():
    @signature_set(_signature())
    async def function():
        return 5

    assert inspect.iscoroutinefunction(function)
    assert asyncio.run(function()) == 5


def test_validation_switch_is_accepted():
    decorator = signature_set(_signature(), _validate_call=False)

    assert decorator(lambda: 1)() == 1
