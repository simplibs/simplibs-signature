from simplibs.exception import ParamError
from simplibs.exception.testing import assert_exception_function

from simplibs.signature.tools.operations._validations import raise_signature_introspection_type_error


def test_raises_the_error_with_its_fields(subtests):
    exc = assert_exception_function(
        subtests,
        raise_signature_introspection_type_error,
        exception_type=ParamError,
        invalid_params=(5, TypeError("not callable")),
        error_name="SIGNATURE INTROSPECTION ERROR",
        label="function",
        value=5,
        expected="a callable supported by inspect.signature()",
        problem="The object type is not supported by inspect.signature().",
        how_to_fix=(
            "Pass a regular function, method, lambda, or class with __call__.",
            "Ensure the object is not a raw C extension or unsupported callable type.",
        ),
        context="inspect.signature() — unsupported callable type",
    )

    assert isinstance(exc, TypeError)
