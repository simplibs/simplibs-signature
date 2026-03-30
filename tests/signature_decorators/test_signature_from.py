"""
Tests for signature_from — decorator factory for assembling signatures from multiple sources.
"""
import inspect
import pytest
from simplibs.signature.signature_decorators.signature_from import signature_from
from simplibs.signature.utils._validations.exceptions.SignatureBuildError import SignatureBuildError
from simplibs.signature.utils._validations.exceptions.SignatureParameterError import SignatureParameterError


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def make_param(name: str, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD) -> inspect.Parameter:
    return inspect.Parameter(name, kind)


def sources_func(c, d): ...


# -----------------------------------------------------------------------------
# Return value
# -----------------------------------------------------------------------------

def test_returns_callable():
    """signature_from must return a callable (the decorator)."""
    decorator = signature_from(make_param("x"))
    assert callable(decorator)


# -----------------------------------------------------------------------------
# Decorated function as base_func
# -----------------------------------------------------------------------------

def test_decorated_function_parameters_are_present():
    """The decorated function's own parameters must appear in the assembled signature."""
    @signature_from()
    def my_func(a, b): ...

    sig = inspect.signature(my_func)
    assert "a" in sig.parameters
    assert "b" in sig.parameters


def test_wrapper_forwards_calls():
    """The wrapper must forward calls to the original function."""
    @signature_from()
    def add(a, b):
        return a + b

    assert add(1, 2) == 3


# -----------------------------------------------------------------------------
# Sources merging
# -----------------------------------------------------------------------------

def test_sources_parameter_is_merged():
    """A parameter from sources must appear in the assembled signature."""
    @signature_from(make_param("z"))
    def my_func(a): ...

    sig = inspect.signature(my_func)
    assert "z" in sig.parameters
    assert "a" in sig.parameters


def test_sources_callable_parameters_are_merged():
    """Parameters from a callable in sources must appear in the assembled signature."""
    @signature_from(sources_func)
    def my_func(a): ...

    sig = inspect.signature(my_func)
    assert "c" in sig.parameters
    assert "d" in sig.parameters
    assert "a" in sig.parameters


# -----------------------------------------------------------------------------
# Ordering
# -----------------------------------------------------------------------------

def test_base_func_first_true_puts_decorated_params_first():
    """With base_func_first=True, decorated function's parameters must precede sources."""
    @signature_from(sources_func, base_func_first=True)
    def my_func(a): ...

    names = list(inspect.signature(my_func).parameters.keys())
    assert names.index("a") < names.index("c")


def test_base_func_first_false_puts_sources_params_first():
    """With base_func_first=False, sources parameters must precede decorated function's."""
    @signature_from(sources_func, base_func_first=False)
    def my_func(a): ...

    names = list(inspect.signature(my_func).parameters.keys())
    assert names.index("c") < names.index("a")


# -----------------------------------------------------------------------------
# return_type
# -----------------------------------------------------------------------------

def test_return_type_unset_inherits_from_decorated_func():
    """return_type=UNSET must inherit the return annotation from the decorated function."""
    @signature_from()
    def my_func(a) -> float: ...

    assert inspect.signature(my_func).return_annotation is float


def test_return_type_explicit_overrides():
    """An explicit return_type must override the decorated function's annotation."""
    @signature_from(return_type=int)
    def my_func(a) -> float: ...

    assert inspect.signature(my_func).return_annotation is int


def test_return_type_none_sets_none():
    """return_type=None must set the return annotation to None."""
    @signature_from(return_type=None)
    def my_func(a) -> float: ...

    assert inspect.signature(my_func).return_annotation is None


# -----------------------------------------------------------------------------
# excluded_names
# -----------------------------------------------------------------------------

def test_excluded_names_are_applied():
    """Parameters matching excluded_names must be absent from the assembled signature."""
    @signature_from(excluded_names=("skip_me",))
    def my_func(a, skip_me): ...

    sig = inspect.signature(my_func)
    assert "skip_me" not in sig.parameters
    assert "a" in sig.parameters


# -----------------------------------------------------------------------------
# accept_double
# -----------------------------------------------------------------------------

def test_accept_double_false_raises_on_duplicate():
    """accept_double=False must raise SignatureBuildError when duplicate parameters appear."""
    with pytest.raises(SignatureBuildError):
        @signature_from(sources_func, accept_double=False)
        def my_func(c): ...


# -----------------------------------------------------------------------------
# Validation — non-callable decorated object
# -----------------------------------------------------------------------------

def test_non_callable_raises_at_decoration_time():
    """Applying the decorator to a non-callable must raise SignatureParameterError."""
    decorator = signature_from(make_param("x"))
    with pytest.raises(SignatureParameterError) as exc_info:
        decorator(42)
    assert isinstance(exc_info.value, TypeError)


def test_no_raises_at_factory_time_for_invalid_decorated_object():
    """signature_from must not raise at factory time — only when the decorator is applied."""
    decorator = signature_from(make_param("x"))
    assert callable(decorator)