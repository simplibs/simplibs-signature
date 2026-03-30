"""
Tests for ProcessParametersMixin — orchestration of base_func, sources, and ordering.
"""
import inspect
import pytest
from simplibs.signature.signature_creator.SignatureCreator import SignatureCreator


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def make_param(name: str, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD) -> inspect.Parameter:
    return inspect.Parameter(name, kind)


def base_func(a, b): ...
def sources_func(c, d): ...


# -----------------------------------------------------------------------------
# Only sources
# -----------------------------------------------------------------------------

def test_only_sources_parameter_appears():
    """When only sources are provided, their parameters must appear in the signature."""
    sc = SignatureCreator(make_param("x"))
    assert "x" in sc.signature.parameters


def test_only_sources_callable_parameters_appear():
    """When only a callable is in sources, its parameters must appear in the signature."""
    sc = SignatureCreator(sources_func)
    assert "c" in sc.signature.parameters
    assert "d" in sc.signature.parameters


# -----------------------------------------------------------------------------
# Only base_func
# -----------------------------------------------------------------------------

def test_only_base_func_parameters_appear():
    """When only base_func is provided, its parameters must appear in the signature."""
    sc = SignatureCreator(base_func=base_func)
    assert "a" in sc.signature.parameters
    assert "b" in sc.signature.parameters


# -----------------------------------------------------------------------------
# Both — base_func_first=True (default)
# -----------------------------------------------------------------------------

def test_base_func_first_true_puts_base_params_before_sources():
    """With base_func_first=True, base_func parameters must precede sources parameters."""
    sc = SignatureCreator(sources_func, base_func=base_func, base_func_first=True)
    names = list(sc.signature.parameters.keys())
    assert names.index("a") < names.index("c")
    assert names.index("b") < names.index("d")


def test_base_func_first_is_default():
    """base_func_first=True must be the default ordering."""
    sc_default = SignatureCreator(sources_func, base_func=base_func)
    sc_explicit = SignatureCreator(sources_func, base_func=base_func, base_func_first=True)
    assert list(sc_default.signature.parameters.keys()) == list(sc_explicit.signature.parameters.keys())


# -----------------------------------------------------------------------------
# Both — base_func_first=False
# -----------------------------------------------------------------------------

def test_base_func_first_false_puts_sources_before_base_params():
    """With base_func_first=False, sources parameters must precede base_func parameters."""
    sc = SignatureCreator(sources_func, base_func=base_func, base_func_first=False)
    names = list(sc.signature.parameters.keys())
    assert names.index("c") < names.index("a")
    assert names.index("d") < names.index("b")


# -----------------------------------------------------------------------------
# All parameters present regardless of order
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("base_func_first", [True, False])
def test_all_parameters_present_regardless_of_order(base_func_first):
    """All parameters from both base_func and sources must be present regardless of order."""
    sc = SignatureCreator(sources_func, base_func=base_func, base_func_first=base_func_first)
    names = sc.signature.parameters.keys()
    assert all(n in names for n in ["a", "b", "c", "d"])