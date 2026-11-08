from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.tools.operations._validations import raise_signature_introspection_value_error


def test_raises_the_error_with_its_fields(subtests):
    exc = assert_exception_function(
        subtests,
        raise_signature_introspection_value_error,
        exception_type=ParamError,
        invalid_params=(len, ValueError("no signature")),
        error_name="SIGNATURE INTROSPECTION ERROR",
        label="function",
        value=len,
        expected="a function with an introspectable signature",
        problem="The function's signature cannot be introspected (e.g. built-in without signature metadata).",
        how_to_fix=(
            "Use a pure Python function or a callable with a defined signature.",
            "Built-in functions like len() or print() may not expose their signature.",
            "If wrapping a built-in, define a wrapper function with an explicit signature.",
        ),
        context="inspect.signature() — signature introspection failed",
    )

    assert isinstance(exc, ValueError)
