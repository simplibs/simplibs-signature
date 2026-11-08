from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.orchestrators._helpers._validations import raise_invalid_parameter_source_error


def test_raises_the_error_with_its_fields(subtests):
    exc = assert_exception_function(
        subtests,
        raise_invalid_parameter_source_error,
        exception_type=ParamError,
        invalid_params=(2, "text"),
        error_name="INVALID PARAMETER SOURCE",
        label="param_sources[2]",
        value="text",
        expected="an inspect.Parameter or a callable (function/method)",
        problem="Item at index 2 is of type 'str', which is not a valid source for parameters.",
        how_to_fix=(
            "Ensure all positional arguments are either Parameter instances or callables.",
            "If you are passing a list of sources, remember to unpack it: create_signature(*my_list).",
            "Use create_keyword_parameter() or create_positional_parameter() to build parameters.",
        ),
        exception=TypeError,
    )

    assert isinstance(exc, TypeError)


def test_names_the_type_of_the_offender(subtests):
    assert_exception_function(
        subtests,
        raise_invalid_parameter_source_error,
        exception_type=ParamError,
        invalid_params=(0, [1, 2]),
        problem="is of type 'list'",
    )
