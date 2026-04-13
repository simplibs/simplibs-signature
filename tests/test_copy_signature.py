"""
Tests for copy_signature — cloning and modifying existing function signatures.
"""
import pytest
import inspect
from typing import Optional, List
from simplibs.sentinels import UNSET

# Imports based on the provided project structure
from src.simplibs.signature.copy_signature import copy_signature
from src.simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

def source_func(a: int, b: str = "default") -> float:
    """Standard source for cloning."""
    return 1.0


def variadic_func(x, *args, **kwargs):
    """Source with variadic parameters."""
    pass


def binding_func(self, cls, x):
    """Source with self/cls parameters."""
    pass


# -----------------------------------------------------------------------------
# Basic Cloning & Return Annotation
# -----------------------------------------------------------------------------

def test_copy_pure_clone():
    """Should create an exact copy of the signature if no modifications are requested."""
    sig = copy_signature(source_func)

    assert list(sig.parameters.keys()) == ["a", "b"]
    assert sig.return_annotation is float
    assert sig.parameters["b"].default == "default"


def test_copy_override_return_annotation():
    """Should replace the return annotation while keeping parameters intact."""
    sig = copy_signature(source_func, return_annotation=int)

    assert sig.return_annotation is int
    assert list(sig.parameters.keys()) == ["a", "b"]


def test_copy_set_return_to_none():
    """Should allow setting return_annotation to None (distinguished from UNSET)."""
    sig = copy_signature(source_func, return_annotation=None)
    assert sig.return_annotation is None


# -----------------------------------------------------------------------------
# Parameter Filtering (Exclusion)
# -----------------------------------------------------------------------------

def test_copy_with_excluded_names():
    """Should remove specific parameters by name."""
    sig = copy_signature(source_func, excluded_names=("a",))

    assert "a" not in sig.parameters
    assert "b" in sig.parameters


def test_copy_exclude_variadic():
    """Should remove *args and **kwargs when include_variadic=False."""
    sig = copy_signature(variadic_func, include_variadic=False)

    assert "x" in sig.parameters
    assert "args" not in sig.parameters
    assert "kwargs" not in sig.parameters


def test_copy_exclude_binding():
    """Should remove 'self' and 'cls' when include_binding=False."""
    sig = copy_signature(binding_func, include_binding=False)

    assert "x" in sig.parameters
    assert "self" not in sig.parameters
    assert "cls" not in sig.parameters


# -----------------------------------------------------------------------------
# Adding & Replacing Parameters
# -----------------------------------------------------------------------------

def test_copy_with_extra_params():
    """Should add new parameters to the end of the signature."""
    new_param = inspect.Parameter("c", inspect.Parameter.KEYWORD_ONLY, annotation=bool)

    sig = copy_signature(source_func, extra_params=(new_param,))

    assert list(sig.parameters.keys()) == ["a", "b", "c"]
    assert sig.parameters["c"].kind == inspect.Parameter.KEYWORD_ONLY


def test_copy_replace_existing_parameter():
    """Should overwrite an existing parameter if a new one with the same name is provided."""
    # Source 'a' is POSITIONAL_OR_KEYWORD: int
    replacement_a = inspect.Parameter("a", inspect.Parameter.KEYWORD_ONLY, annotation=str)

    sig = copy_signature(source_func, extra_params=(replacement_a,))

    assert sig.parameters["a"].annotation is str
    assert sig.parameters["a"].kind == inspect.Parameter.KEYWORD_ONLY


# -----------------------------------------------------------------------------
# Validation & Errors
# -----------------------------------------------------------------------------

def test_copy_raises_on_invalid_extra_params():
    """Should raise SignatureParameterError if extra_params contains non-Parameter objects."""
    with pytest.raises(SignatureParameterError):
        # Passing a string instead of inspect.Parameter
        copy_signature(source_func, extra_params=("not_a_param",))  # type: ignore


def test_copy_raises_on_invalid_function():
    """Should raise an error if the first argument is not a callable."""
    with pytest.raises(Exception):  # Exact exception depends on get_signature implementation
        copy_signature("not_a_function")  # type: ignore


def test_copy_respects_accept_double_false():
    """Should raise SignatureBuildError if names collide and accept_double is False."""
    collision_param = inspect.Parameter("a", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    with pytest.raises(SignatureBuildError):
        copy_signature(source_func, extra_params=(collision_param,), accept_double=False)


# -----------------------------------------------------------------------------
# Flat Mode Integration
# -----------------------------------------------------------------------------

def test_copy_signature_flat_mode_integration():
    """
    Verify that flat_to_kwargs converts both parameters from the source
    function and extra_params to KEYWORD_ONLY.
    """

    # Using a dedicated local function to make the test self-contained
    def local_source(a, b=1):
        pass

    extra_p = inspect.Parameter("c", inspect.Parameter.POSITIONAL_ONLY)

    sig = copy_signature(
        local_source,
        extra_params=[extra_p],
        flat_to_kwargs=True
    )

    # Check that all (original a, b and extra c) are now KEYWORD_ONLY
    assert len(sig.parameters) == 3
    for name in ["a", "b", "c"]:
        assert sig.parameters[name].kind == inspect.Parameter.KEYWORD_ONLY


def test_copy_signature_raises_on_invalid_flat_to_kwargs_type():
    """Should raise SignatureParameterError if flat_to_kwargs is not a boolean."""

    def f(): pass

    with pytest.raises(SignatureParameterError):
        copy_signature(f, flat_to_kwargs="invalid")  # type: ignore