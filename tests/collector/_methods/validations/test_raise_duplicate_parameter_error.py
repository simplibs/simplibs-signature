import inspect

from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function
from simplibs.exception.testing.tools import Kwargs

from simplibs.signature.collector._methods.validations import raise_duplicate_parameter_error

EXPECTED = "a unique parameter name"


def test_same_name(subtests, make_param):
    exc = assert_exception_function(
        subtests,
        raise_duplicate_parameter_error,
        exception_type=ParamError,
        invalid_params=(make_param("x"),),
        error_name="DUPLICATE PARAMETER ERROR",
        label="param.name",
        value="x",
        expected=EXPECTED,
        problem="Parameter 'x' is already defined in this signature.",
        how_to_fix=(
            "Ensure that the parameter name 'x' is unique within the signature.",
            "If you intend to overwrite existing parameters, set 'accept_double=True' in the collector.",
            "Check if you are accidentally adding the same source or function multiple times.",
        ),
        exception=ValueError,
    )

    assert isinstance(exc, ValueError)


def test_existing_name_equal_to_the_new_one_is_an_ordinary_collision(subtests, make_param):
    assert_exception_function(
        subtests,
        raise_duplicate_parameter_error,
        exception_type=ParamError,
        invalid_params=Kwargs(param=make_param("x"), existing_name="x"),
        value="x",
        problem="Parameter 'x' is already defined in this signature.",
    )


def test_second_variadic_positional_names_the_stored_one(subtests, make_param):
    assert_exception_function(
        subtests,
        raise_duplicate_parameter_error,
        exception_type=ParamError,
        invalid_params=(make_param("b", inspect.Parameter.VAR_POSITIONAL), "a"),
        value="b",
        problem="collides with the already defined variadic positional parameter 'a'",
        expected=EXPECTED,
    )


def test_second_variadic_keyword_names_the_stored_one(subtests, make_param):
    assert_exception_function(
        subtests,
        raise_duplicate_parameter_error,
        exception_type=ParamError,
        invalid_params=(make_param("options", inspect.Parameter.VAR_KEYWORD), "kwargs"),
        value="options",
        problem="collides with the already defined variadic keyword parameter 'kwargs'",
    )
