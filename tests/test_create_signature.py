"""
Tests for create_signature — the universal entry-point and smart dispatcher.
Supports Iterable types for excluded_names across both dispatch paths.
"""
import pytest
import inspect
from typing import Optional, List
from simplibs.sentinels import UNSET

# Imports based on the provided project structure
from src.simplibs.signature.create_signature import create_signature
from src.simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

def alpha_func(a: int, b: str = "default") -> float:
    """First source function."""
    return 1.0

def beta_func(c: bool) -> str:
    """Second source function."""
    return "done"

@pytest.fixture
def param_d():
    """A standalone inspect.Parameter with a default to follow 'b' safely."""
    return inspect.Parameter(
        "d",
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=int,
        default=0
    )


# -----------------------------------------------------------------------------
# Fast Path (Single Callable) — Iterable Support
# -----------------------------------------------------------------------------

def test_create_fast_path_simple_clone():
    """Should correctly dispatch to copy_signature when a single callable is provided."""
    sig = create_signature(alpha_func)

    assert list(sig.parameters.keys()) == ["a", "b"]
    assert sig.return_annotation is float


@pytest.mark.parametrize("collection_type", [list, tuple, set])
def test_create_fast_path_with_modifications_iterables(collection_type):
    """Should allow modifications (return_source, exclusions) using various iterables in Fast Path."""
    excludes = collection_type(["b"])
    sig = create_signature(
        alpha_func,
        return_source=int,
        excluded_names=excludes
    )

    assert list(sig.parameters.keys()) == ["a"]
    assert "b" not in sig.parameters
    assert sig.return_annotation is int


def test_create_fast_path_with_generator_exclusion():
    """Should correctly handle generator in excluded_names within the Fast Path."""
    gen_excludes = (name for name in ["a"])
    sig = create_signature(alpha_func, excluded_names=gen_excludes)

    assert "a" not in sig.parameters
    assert "b" in sig.parameters


# -----------------------------------------------------------------------------
# Standard Path (Multiple Sources / Parameters) — Iterable Support
# -----------------------------------------------------------------------------

def test_create_standard_path_multiple_callables_with_list_exclusion():
    """Should use SignatureCreator and respect list-based excluded_names in Standard Path."""
    # Sources: alpha_func (a, b) + beta_func (c)
    sig = create_signature(alpha_func, beta_func, excluded_names=["b", "c"])

    assert list(sig.parameters.keys()) == ["a"]
    assert "b" not in sig.parameters
    assert "c" not in sig.parameters


def test_create_standard_path_mixed_sources(param_d):
    """Should merge callables and standalone Parameter objects."""
    sig = create_signature(alpha_func, param_d)

    assert list(sig.parameters.keys()) == ["a", "b", "d"]
    assert sig.parameters["d"].annotation is int


# -----------------------------------------------------------------------------
# Edge Cases & Special Dispatching
# -----------------------------------------------------------------------------

def test_create_with_single_parameter_object(param_d):
    """
    Should use Standard Path (SignatureCreator) when only a single Parameter
    is provided (not a callable).
    """
    sig = create_signature(param_d)
    assert list(sig.parameters.keys()) == ["d"]


def test_create_preserves_complex_return_source():
    """Should handle complex typing as return_source across both paths."""
    complex_type = Optional[List[str]]

    # Fast path - it doesn't matter here, there is only one function
    sig_fast = create_signature(alpha_func, return_source=complex_type)
    assert sig_fast.return_annotation == complex_type

    # Standard path - swap the order so that the mandatory parameters from beta_func
    # are before the default parameters from alpha_func
    sig_std = create_signature(beta_func, alpha_func, return_source=complex_type)
    assert sig_std.return_annotation == complex_type


# -----------------------------------------------------------------------------
# Validation & Error Handling
# -----------------------------------------------------------------------------

def test_create_raises_on_empty_sources():
    """Should raise SignatureBuildError if no param_sources are provided."""
    with pytest.raises(SignatureBuildError):
        create_signature()


def test_create_raises_on_invalid_excluded_names_string_trap():
    """Should raise SignatureParameterError if excluded_names is a raw string (String Trap)."""
    with pytest.raises(SignatureParameterError):
        create_signature(alpha_func, excluded_names="a") # type: ignore


def test_create_raises_on_invalid_types_in_sources():
    """Should raise SignatureBuildError if sources contain invalid types."""
    with pytest.raises(SignatureBuildError):
        create_signature(alpha_func, "not-a-parameter-or-callable") # type: ignore


def test_create_raises_on_invalid_config_type():
    """Should raise SignatureParameterError if boolean flags are not booleans."""
    with pytest.raises(SignatureParameterError):
        create_signature(alpha_func, accept_double="not-a-bool") # type: ignore


def test_create_respects_validate_flag():
    """Should bypass initial validation if validate=False."""
    # When validate=False, the string trap or boolean check is skipped at entry.
    try:
        create_signature(alpha_func, accept_double="invalid", validate=False) # type: ignore
    except (TypeError, ValueError, SignatureBuildError):
        pass


# -----------------------------------------------------------------------------
# Flat Mode Integration (Cross-Path Verification)
# -----------------------------------------------------------------------------

def test_create_signature_flat_mode_fast_path():
    """Verify flat_to_kwargs works in the Fast Path (single callable)."""

    def local_func(a, b=1): pass

    sig = create_signature(local_func, flat_to_kwargs=True)

    assert len(sig.parameters) == 2
    for param in sig.parameters.values():
        assert param.kind == inspect.Parameter.KEYWORD_ONLY


def test_create_signature_flat_mode_standard_path(param_d):
    """Verify flat_to_kwargs works in the Standard Path (multiple sources)."""
    # Sources: beta_func (c: bool) + param_d (d=0)
    sig = create_signature(beta_func, param_d, flat_to_kwargs=True)

    assert len(sig.parameters) == 2
    assert sig.parameters["c"].kind == inspect.Parameter.KEYWORD_ONLY
    assert sig.parameters["d"].kind == inspect.Parameter.KEYWORD_ONLY


def test_create_signature_raises_on_invalid_flat_to_kwargs_type():
    """Should raise SignatureParameterError if flat_to_kwargs is not a boolean."""
    with pytest.raises(SignatureParameterError):
        create_signature(alpha_func, flat_to_kwargs="not-a-bool")  # type: ignore