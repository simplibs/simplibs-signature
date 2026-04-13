"""
Tests for SignatureCreator — the high-level orchestrator for building inspect.Signature objects.
"""
import pytest
import inspect
from typing import Callable, List, Optional
from simplibs.sentinels import UNSET

# Imports based on the provided project structure
from src.simplibs.signature.core.signature_creator.SignatureCreator import SignatureCreator
from src.simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError
from src.simplibs.signature.core.validators.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Fixtures & Helpers
# -----------------------------------------------------------------------------

def func_source(a: int, b: str = "default") -> float:
    """A sample source function."""
    return 1.0


def another_func(c: bool, **kwargs):
    """Another source function with variadic arguments."""
    pass


@pytest.fixture
def param_x():
    """A standalone inspect.Parameter."""
    return inspect.Parameter(
        "x",
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=int,
        default=123
    )


# -----------------------------------------------------------------------------
# Basic Orchestration
# -----------------------------------------------------------------------------

def test_creator_initialization_with_mixed_sources(param_x):
    """Should merge a function source and a standalone parameter into one signature."""
    # Source: func_source (a, b) + param_x (x)
    creator = SignatureCreator(func_source, param_x, return_source=int)
    sig = creator.signature

    assert isinstance(sig, inspect.Signature)
    assert list(sig.parameters.keys()) == ["a", "b", "x"]
    assert sig.return_annotation is int


def test_creator_extracts_return_from_source():
    """Should automatically extract return annotation if return_source is a callable."""
    creator = SignatureCreator(func_source, return_source=func_source)
    assert creator.signature.return_annotation is float


def test_creator_default_return_is_empty():
    """Should result in an empty return annotation if no return_source is provided."""
    creator = SignatureCreator(func_source)
    assert creator.signature.return_annotation is inspect.Signature.empty

def test_creator_integration_with_flat_mode():
    """Should transform all parameters to KEYWORD_ONLY when flat_to_kwargs is True."""
    # Source has: a (POS_OR_KW), b (POS_OR_KW)
    creator = SignatureCreator(func_source, flat_to_kwargs=True)
    sig = creator.signature

    assert len(sig.parameters) == 2
    for param in sig.parameters.values():
        assert param.kind == inspect.Parameter.KEYWORD_ONLY

# -----------------------------------------------------------------------------
# Filtering & Deduplication Rules (Iterable Support)
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("collection_type", [list, tuple, set])
def test_creator_respects_excluded_names_various_types(collection_type):
    """Should skip parameters specified in excluded_names using various iterable types."""
    excludes = collection_type(["b"])
    creator = SignatureCreator(func_source, excluded_names=excludes)

    assert "a" in creator.signature.parameters
    assert "b" not in creator.signature.parameters


def test_creator_respects_excluded_names_generator():
    """Should skip parameters when excluded_names is provided as a generator."""
    def gen_excludes():
        yield "b"

    creator = SignatureCreator(func_source, excluded_names=gen_excludes())
    assert "b" not in creator.signature.parameters


def test_creator_respects_include_variadic():
    """Should filter out *args and **kwargs when include_variadic=False."""
    creator = SignatureCreator(another_func, include_variadic=False)
    assert "c" in creator.signature.parameters
    assert "kwargs" not in creator.signature.parameters


def test_creator_replaces_duplicates_by_default(param_x):
    """Should overwrite earlier parameters with later ones if they share the same name."""
    # Define a parameter with the same name 'a' as in func_source
    new_a = inspect.Parameter("a", inspect.Parameter.KEYWORD_ONLY, annotation=str)

    creator = SignatureCreator(func_source, new_a)

    # The 'a' from new_a should win
    param_a = creator.signature.parameters["a"]
    assert param_a.kind == inspect.Parameter.KEYWORD_ONLY
    assert param_a.annotation is str


# -----------------------------------------------------------------------------
# Complex Scenarios & Typing
# -----------------------------------------------------------------------------

def test_creator_handles_complex_typing_as_return_source():
    """Should correctly handle Optional/Union as return_source."""
    complex_type = Optional[List[str]]
    creator = SignatureCreator(func_source, return_source=complex_type)

    assert creator.signature.return_annotation == complex_type


def test_creator_with_multiple_callables():
    """Should merge parameters from multiple callables in order."""

    def first(a): pass

    def second(b): pass

    creator = SignatureCreator(first, second)
    assert list(creator.signature.parameters.keys()) == ["a", "b"]


# -----------------------------------------------------------------------------
# Validation & Error Handling
# -----------------------------------------------------------------------------

def test_creator_raises_on_invalid_param_source():
    """Should raise SignatureBuildError when an invalid source type is passed."""
    with pytest.raises(SignatureBuildError):
        SignatureCreator(123)  # type: ignore (int is not a valid source)


def test_creator_raises_on_invalid_excluded_names():
    """Should raise SignatureParameterError for non-iterable or string excluded_names."""
    # Testing the "string trap" - passing a string instead of a collection
    with pytest.raises(SignatureParameterError):
        SignatureCreator(func_source, excluded_names="b") # type: ignore


def test_creator_raises_on_invalid_config_type():
    """Should raise SignatureParameterError if boolean flags are not booleans."""
    with pytest.raises(SignatureParameterError):
        SignatureCreator(func_source, accept_double="not-a-bool")  # type: ignore


def test_creator_validation_bypass():
    """Should skip initial validation if validate=False."""
    # When bypass is active, it shouldn't raise SignatureParameterError
    # but might fail deeper with a different error later during processing
    try:
        SignatureCreator(func_source, accept_double="invalid", validate=False)  # type: ignore
    except (TypeError, ValueError, SignatureBuildError):
        pass

def test_creator_raises_on_invalid_flat_to_kwargs_type():
    """Should raise SignatureParameterError if flat_to_kwargs is not a boolean."""
    with pytest.raises(SignatureParameterError):
        SignatureCreator(func_source, flat_to_kwargs="not-a-bool")  # type: ignore