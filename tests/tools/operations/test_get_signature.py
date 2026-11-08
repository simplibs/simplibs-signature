import inspect

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs

from simplibs.signature import get_signature


def _function(a, b=1, *args, c, **kwargs) -> int:
    ...


class _Thing:
    def __init__(self, x, y=2): ...

    def method(self, z): ...


def _looped():
    ...


_looped.__wrapped__ = _looped  # inspect.signature cannot unwrap this: ValueError


@pytest.mark.parametrize("function", [_function, _Thing, _Thing.method, _Thing(1).method, lambda q, r=3: None])
def test_gives_what_inspect_gives(function):
    assert get_signature(function) == inspect.signature(function)


def test_validation_switch_is_accepted():
    assert get_signature(_function, _validate_call=False) == inspect.signature(_function)


def test_a_signature_that_cannot_be_read_is_refused(subtests):
    exc = assert_exception_function(
        subtests,
        get_signature,
        exception_type=ParamError,
        invalid_params=(_looped,),
        valid_params=(_function,),
        error_name="SIGNATURE INTROSPECTION ERROR",
        label="function",
        value=_looped,
        expected="a function with an introspectable signature",
    )

    assert isinstance(exc, ValueError)


def test_something_that_is_not_a_callable_is_refused(subtests):
    exc = assert_exception_function(
        subtests,
        get_signature,
        exception_type=ParamError,
        invalid_params=Kwargs(function=5, _validate_call=False),
        error_name="SIGNATURE INTROSPECTION ERROR",
        label="function",
        value=5,
        expected="a callable supported by inspect.signature()",
    )

    assert isinstance(exc, TypeError)
