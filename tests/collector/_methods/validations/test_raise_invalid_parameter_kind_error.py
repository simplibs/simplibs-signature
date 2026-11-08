from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.collector._methods.validations import raise_invalid_parameter_kind_error


def test_raises_the_error_with_its_fields(subtests, make_param):
    param = make_param("x")

    exc = assert_exception_function(
        subtests,
        raise_invalid_parameter_kind_error,
        exception_type=ParamError,
        invalid_params=(param, KeyError("kind")),
        error_name="INVALID PARAMETER KIND ERROR",
        label="param.kind",
        value=param.kind,
        expected="a valid inspect._ParameterKind enum value",
        problem="Parameter 'x' has an unsupported kind",
        how_to_fix="Ensure you are using standard Python parameter kinds.",
    )

    assert isinstance(exc, ParamError)


def test_keeps_the_type_of_the_original_error(subtests, make_param):
    exc = assert_exception_function(
        subtests,
        raise_invalid_parameter_kind_error,
        exception_type=ParamError,
        invalid_params=(make_param("x"), KeyError("kind")),
        deep_check=False,
    )

    assert isinstance(exc, KeyError)
