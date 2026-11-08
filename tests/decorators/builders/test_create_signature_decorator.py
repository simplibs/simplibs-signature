import asyncio
import inspect

from simplibs.signature import create_signature_decorator

P = inspect.Parameter


def _signature():
    return inspect.Signature([P("only", P.KEYWORD_ONLY)])


def test_decorates_with_the_fixed_signature():
    decorator = create_signature_decorator(_signature())

    @decorator
    def function(a, b):
        return a + b

    assert inspect.signature(function) == _signature()
    assert function(1, 2) == 3


def test_one_decorator_serves_many_functions():
    decorator = create_signature_decorator(_signature())

    first = decorator(lambda: 1)
    second = decorator(lambda: 2)

    assert inspect.signature(first) == inspect.signature(second) == _signature()
    assert (first(), second()) == (1, 2)


def test_works_for_a_coroutine_function():
    @create_signature_decorator(_signature())
    async def function():
        return "done"

    assert inspect.iscoroutinefunction(function)
    assert asyncio.run(function()) == "done"


def test_validation_switch_is_accepted():
    decorator = create_signature_decorator(_signature(), _validate_call=False)

    assert decorator(lambda: 1)() == 1
