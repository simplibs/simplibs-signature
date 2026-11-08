from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.tools.operations._validations import raise_signature_composition_value_error


def test_raises_the_error_with_its_fields(subtests):
    parameters = (1, 2)

    exc = assert_exception_function(
        subtests,
        raise_signature_composition_value_error,
        exception_type=ParamError,
        invalid_params=(parameters, ValueError("bad order")),
        error_name="SIGNATURE COMPOSITION ERROR",
        label="parameters",
        value=parameters,
        expected="a collection of valid, uniquely named inspect.Parameter instances",
        problem="One or more parameters are structurally invalid (e.g. duplicates or wrong order).",
        how_to_fix=(
            "Ensure all parameter names are unique.",
            "Check that order follows: POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, *args, KEYWORD_ONLY, **kwargs.",
            "Verify that each parameter is a valid inspect.Parameter instance.",
        ),
        context="inspect.Signature() — invalid parameter structure",
    )

    assert isinstance(exc, ValueError)
