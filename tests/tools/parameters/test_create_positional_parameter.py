import inspect

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs

from simplibs.signature import create_positional_parameter


def test_builds_an_ordinary_parameter_by_default():
    param = create_positional_parameter("x", annotation=int, default=3)

    assert isinstance(param, inspect.Parameter)
    assert (param.name, param.kind, param.annotation, param.default) == (
        "x", inspect.Parameter.POSITIONAL_OR_KEYWORD, int, 3,
    )


def test_positional_only_flag():
    param = create_positional_parameter("x", positional_only=True)

    assert param.kind is inspect.Parameter.POSITIONAL_ONLY


def test_defaults_to_required_and_unannotated():
    param = create_positional_parameter("x")

    assert param.default is inspect.Parameter.empty
    assert param.annotation is inspect.Parameter.empty


def test_annotation_and_default_must_be_named():
    with pytest.raises(TypeError):
        create_positional_parameter("x", int)


@pytest.mark.parametrize("positional_only", [False, True])
def test_a_default_that_contradicts_the_annotation_is_refused(subtests, positional_only):
    exc = assert_exception_function(
        subtests,
        create_positional_parameter,
        exception_type=ParamError,
        invalid_params=Kwargs(name="x", annotation=int, default="text", positional_only=positional_only),
        valid_params=Kwargs(name="x", annotation=int, default=1, positional_only=positional_only),
        error_name="INVALID DEFAULT VALUE",
        value="text",
    )

    assert isinstance(exc, TypeError)


def test_validation_switch_skips_the_default_check():
    param = create_positional_parameter("x", annotation=int, default="text", _validate_call=False)

    assert param.default == "text"
