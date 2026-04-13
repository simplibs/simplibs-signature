"""
Tests for add_params_to_signature — extending existing signatures with new parameters.
"""
import pytest
import inspect
from typing import Any

# Imports based on the provided project structure
from src.simplibs.signature.core.utils.modifiers.add_params_to_signature import add_params_to_signature
from src.simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

@pytest.fixture
def base_signature():
    """Provides a signature: (a, b=1) -> int"""
    p1 = inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD)
    p2 = inspect.Parameter("b", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=1)
    return inspect.Signature(parameters=(p1, p2), return_annotation=int)


# -----------------------------------------------------------------------------
# Basic Addition & Ordering (Iterable support)
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("collection_type", [tuple, list])
def test_add_params_success(base_signature, collection_type):
    """Should add new parameters from various iterable types and maintain correct Python order."""
    # Adding a keyword-only and a positional-only parameter
    p_pos = inspect.Parameter("p", inspect.Parameter.POSITIONAL_ONLY)
    p_kwo = inspect.Parameter("k", inspect.Parameter.KEYWORD_ONLY)

    # Testing with both tuple and list
    new_sig = add_params_to_signature(base_signature, collection_type([p_kwo, p_pos]))

    # Order must be: p (POS_ONLY) -> a, b (POS_OR_KW) -> k (KWO)
    names = list(new_sig.parameters.keys())
    assert names == ["p", "a", "b", "k"]
    assert new_sig.return_annotation is int


def test_add_params_with_generator(base_signature):
    """Should successfully add parameters even when passed as a one-time generator."""
    p_new = inspect.Parameter("gen_param", inspect.Parameter.KEYWORD_ONLY)

    def param_generator():
        yield p_new

    new_sig = add_params_to_signature(base_signature, param_generator())

    assert "gen_param" in new_sig.parameters
    assert isinstance(new_sig.parameters["gen_param"], inspect.Parameter)


def test_add_variadic_parameters(base_signature):
    """Should successfully add *args and **kwargs."""
    args = inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL)
    kwargs = inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD)

    new_sig = add_params_to_signature(base_signature, (kwargs, args))

    names = list(new_sig.parameters.keys())
    assert names == ["a", "b", "args", "kwargs"]


# -----------------------------------------------------------------------------
# Duplicate Handling (accept_double, replace_double)
# -----------------------------------------------------------------------------

def test_replace_existing_parameter(base_signature):
    """Should replace existing parameter with new definition and maintain valid default order."""
    new_a = inspect.Parameter(
        "a",
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=str,
        default="new_default"
    )

    new_sig = add_params_to_signature(base_signature, [new_a], replace_double=True)

    assert new_sig.parameters["a"].annotation is str
    assert new_sig.parameters["a"].default == "new_default"


def test_keep_existing_parameter(base_signature):
    """Should keep original parameter when replace_double=False."""
    new_a = inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str)

    new_sig = add_params_to_signature(base_signature, (new_a,), replace_double=False)

    # Should still be the original 'a' (no annotation)
    assert new_sig.parameters["a"].annotation is inspect.Parameter.empty


def test_collision_raises_error(base_signature):
    """Should raise SignatureBuildError when accept_double=False and collision occurs."""
    new_a = inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    with pytest.raises(SignatureBuildError):
        add_params_to_signature(base_signature, [new_a], accept_double=False)


# -----------------------------------------------------------------------------
# Validation & Structural Errors
# -----------------------------------------------------------------------------

def test_invalid_input_types_raises():
    """Should raise SignatureParameterError for non-iterable input (when validate=True)."""
    with pytest.raises(SignatureParameterError) as exc_info:
        # Second arg not iterable
        add_params_to_signature(inspect.Signature(), 123)  # type: ignore

    assert "must be iterable" in str(exc_info.value.problem)


def test_structural_violation_raises(base_signature):
    """Should raise SignatureBuildError if resulting structure is invalid (e.g. invalid order)."""
    # Placing a positional parameter after a keyword-only (handled by ParameterCollector/Signature.replace)
    # Here we use an invalid item to trigger the specific catch block
    with pytest.raises(SignatureBuildError):
        add_params_to_signature(base_signature, [None], validate=False)  # type: ignore


# -----------------------------------------------------------------------------
# Immutability & Skip Validation
# -----------------------------------------------------------------------------

def test_original_signature_is_not_modified(base_signature):
    """Verify that the original signature remains unchanged (immutability)."""
    p_new = inspect.Parameter("new", inspect.Parameter.KEYWORD_ONLY)
    add_params_to_signature(base_signature, [p_new])

    assert "new" not in base_signature.parameters


def test_skip_validation_bypass(base_signature):
    """Should skip type checks when validate=False but still catch structural errors from replace()."""
    with pytest.raises(SignatureBuildError) as exc_info:
        add_params_to_signature(
            base_signature,
            ["not_a_parameter_obj"],  # type: ignore
            validate=False
        )
    assert exc_info.value.error_name in ["SIGNATURE TYPE ERROR", "INVALID PARAMETER TYPE"]


# -----------------------------------------------------------------------------
# Flat Mode Integration
# -----------------------------------------------------------------------------

def test_add_params_flat_mode_integration(base_signature):
    """
    Verify that flat_to_kwargs converts both existing parameters from the
    base signature and the newly added parameters to KEYWORD_ONLY.
    """
    # New parameter that is normally POSITIONAL_ONLY
    p_new = inspect.Parameter("p_new", inspect.Parameter.POSITIONAL_ONLY)

    # Base signature has "a" and "b" as POSITIONAL_OR_KEYWORD
    new_sig = add_params_to_signature(
        base_signature,
        [p_new],
        flat_to_kwargs=True
    )

    # All parameters (existing and new) must be KEYWORD_ONLY
    for name in ["a", "b", "p_new"]:
        assert new_sig.parameters[name].kind == inspect.Parameter.KEYWORD_ONLY


def test_add_params_raises_on_invalid_flat_to_kwargs_type(base_signature):
    """Should raise SignatureParameterError if flat_to_kwargs is not a boolean."""
    with pytest.raises(SignatureParameterError):
        add_params_to_signature(
            base_signature,
            [],
            flat_to_kwargs="not-a-bool"  # type: ignore
        )