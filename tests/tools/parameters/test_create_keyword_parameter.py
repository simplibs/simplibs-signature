import inspect

import pytest
from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs

from simplibs.signature import create_keyword_parameter


def test_builds_a_keyword_only_parameter():
    param = create_keyword_parameter("x", annotation=int, default=3)

    assert isinstance(param, inspect.Parameter)
    assert (param.name, param.kind, param.annotation, param.default) == (
        "x", inspect.Parameter.KEYWORD_ONLY, int, 3,
    )


def test_defaults_to_required_and_unannotated():
    param = create_keyword_parameter("x")

    assert param.default is inspect.Parameter.empty
    assert param.annotation is inspect.Parameter.empty


def test_annotation_and_default_must_be_named():
    with pytest.raises(TypeError):
        create_keyword_parameter("x", int)


def test_a_default_that_contradicts_the_annotation_is_refused(subtests):
    exc = assert_exception_function(
        subtests,
        create_keyword_parameter,
        exception_type=ParamError,
        invalid_params=Kwargs(name="x", annotation=int, default="text"),
        valid_params=Kwargs(name="x", annotation=int, default=1),
        error_name="INVALID DEFAULT VALUE",
        value="text",
    )

    assert isinstance(exc, TypeError)


def test_none_is_always_an_acceptable_default():
    assert create_keyword_parameter("x", annotation=int, default=None).default is None


def test_validation_switch_skips_the_default_check():
    param = create_keyword_parameter("x", annotation=int, default="text", _validate_call=False)

    assert param.default == "text"
