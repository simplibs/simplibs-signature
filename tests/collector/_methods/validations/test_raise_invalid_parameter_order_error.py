from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.collector._methods.validations import raise_invalid_parameter_order_error


def test_raises_the_error_with_its_fields(subtests, make_param):
    exc = assert_exception_function(
        subtests,
        raise_invalid_parameter_order_error,
        exception_type=ParamError,
        invalid_params=(make_param("x"),),
        error_name="INVALID PARAMETER ORDER",
        label="param.name",
        value="x",
        expected="non-default parameters before default parameters",
        problem="Parameter 'x' (no default value) cannot follow parameters that already have default values.",
        how_to_fix=(
            "Ensure all mandatory parameters (without defaults) are added before optional parameters (with defaults).",
            "Check the order of your sources or extra_params.",
        ),
        exception=SyntaxError,
    )

    assert isinstance(exc, SyntaxError)
