import inspect

from simplibs.signature import ARGS
from simplibs.signature.constants import ARGS as ARGS_FROM_PACKAGE


def test_is_a_variadic_positional_parameter():
    assert isinstance(ARGS, inspect.Parameter)
    assert ARGS.name == "args"
    assert ARGS.kind is inspect.Parameter.VAR_POSITIONAL


def test_has_no_default_and_no_annotation():
    assert ARGS.default is inspect.Parameter.empty
    assert ARGS.annotation is inspect.Parameter.empty


def test_is_the_same_object_from_the_root_and_the_package():
    assert ARGS is ARGS_FROM_PACKAGE


def test_forms_a_signature():
    assert str(inspect.Signature([ARGS])) == "(*args)"
