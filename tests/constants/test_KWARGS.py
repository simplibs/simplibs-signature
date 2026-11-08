import inspect

from simplibs.signature import KWARGS
from simplibs.signature.constants import KWARGS as KWARGS_FROM_PACKAGE


def test_is_a_variadic_keyword_parameter():
    assert isinstance(KWARGS, inspect.Parameter)
    assert KWARGS.name == "kwargs"
    assert KWARGS.kind is inspect.Parameter.VAR_KEYWORD


def test_has_no_default_and_no_annotation():
    assert KWARGS.default is inspect.Parameter.empty
    assert KWARGS.annotation is inspect.Parameter.empty


def test_is_the_same_object_from_the_root_and_the_package():
    assert KWARGS is KWARGS_FROM_PACKAGE


def test_forms_a_signature():
    assert str(inspect.Signature([KWARGS])) == "(**kwargs)"
