"""
Tests for delete_params_from_signature — pruning signatures by removing parameters by name.
Supports various iterable types for excluded_names.
"""
import pytest
import inspect

# Imports based on the provided project structure
from src.simplibs.signature.core.utils.modifiers.delete_params_from_signature import delete_params_from_signature
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

@pytest.fixture
def complex_signature():
    """Provides a signature: (a, b=1, *args, k=None, **kwargs)"""
    return inspect.Signature(parameters=(
        inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD),
        inspect.Parameter("b", inspect.Parameter.POSITIONAL_OR_KEYWORD, default=1),
        inspect.Parameter("args", inspect.Parameter.VAR_POSITIONAL),
        inspect.Parameter("k", inspect.Parameter.KEYWORD_ONLY, default=None),
        inspect.Parameter("kwargs", inspect.Parameter.VAR_KEYWORD),
    ))


# -----------------------------------------------------------------------------
# Basic Deletion & Iterable Support
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("collection_type", [list, tuple, set])
def test_delete_single_parameter_various_iterables(complex_signature, collection_type):
    """Should remove a single parameter using different iterable types."""
    # Testing list, tuple, and set support
    excludes = collection_type(["b"])
    new_sig = delete_params_from_signature(complex_signature, excludes)

    assert "b" not in new_sig.parameters
    assert list(new_sig.parameters.keys()) == ["a", "args", "k", "kwargs"]


def test_delete_multiple_parameters_generator(complex_signature):
    """Should remove multiple parameters using a generator expression."""
    # Testing generator support
    gen_excludes = (name for name in ["args", "kwargs"])
    new_sig = delete_params_from_signature(complex_signature, gen_excludes)

    assert "args" not in new_sig.parameters
    assert "kwargs" not in new_sig.parameters
    assert list(new_sig.parameters.keys()) == ["a", "b", "k"]


# -----------------------------------------------------------------------------
# Edge Cases & Behavior
# -----------------------------------------------------------------------------

def test_delete_non_existent_name(complex_signature):
    """Should silently ignore names that are not present in the signature."""
    # Name 'z' is not present in the signature
    new_sig = delete_params_from_signature(complex_signature, ["z"])

    # Signature should remain identical in content
    assert len(new_sig.parameters) == len(complex_signature.parameters)
    assert list(new_sig.parameters.keys()) == list(complex_signature.parameters.keys())


def test_delete_all_parameters(complex_signature):
    """Should return an empty signature if all parameters are excluded."""
    all_names = list(complex_signature.parameters.keys())
    new_sig = delete_params_from_signature(complex_signature, all_names)

    assert len(new_sig.parameters) == 0


def test_original_signature_immutability(complex_signature):
    """Verify that the original signature is not modified (immutability check)."""
    delete_params_from_signature(complex_signature, ["a"])
    assert "a" in complex_signature.parameters


# -----------------------------------------------------------------------------
# Validation Errors
# -----------------------------------------------------------------------------

def test_invalid_signature_type_raises():
    """Should raise SignatureParameterError if signature is not an inspect.Signature."""
    with pytest.raises(SignatureParameterError):
        delete_params_from_signature("not_a_signature", ["a"]) # type: ignore


def test_invalid_excluded_names_type_raises(complex_signature):
    """Should raise SignatureParameterError if excluded_names is a string (String Trap)."""
    with pytest.raises(SignatureParameterError):
        # Passing a raw string instead of a collection
        delete_params_from_signature(complex_signature, "a") # type: ignore


def test_skip_validation_bypass(complex_signature):
    """Should skip type checks when validate=False."""
    # This should bypass our guard and proceed to Collector
    new_sig = delete_params_from_signature(
        complex_signature,
        [123], # type: ignore (not a string, but in a list)
        validate=False
    )
    # Collector should simply not find any match for 123, leaving signature as is
    assert len(new_sig.parameters) == len(complex_signature.parameters)