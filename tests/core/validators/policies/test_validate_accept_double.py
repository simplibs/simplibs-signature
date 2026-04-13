"""
Tests for validate_accept_double — verifying duplicate detection logic
and error metadata for SignatureBuildError.
"""
import pytest
import inspect
# Target function and exception
from simplibs.signature.core.validators._policies.validate_accept_double import validate_accept_double
from simplibs.signature.core.validators.exceptions.SignatureBuildError import SignatureBuildError


# -----------------------------------------------------------------------------
# Valid Cases (No Exception)
# -----------------------------------------------------------------------------

def test_accept_double_true_passes_silently():
    """If accept_double is True, the function must pass without raising anything."""
    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    # This should not raise any exception
    validate_accept_double(param, accept_double=True)


# -----------------------------------------------------------------------------
# Invalid Cases (Exceptions)
# -----------------------------------------------------------------------------

def test_accept_double_false_raises_signature_build_error():
    """
    If accept_double is False, it must raise SignatureBuildError 
    with ValueError as the underlying exception.
    """
    param = inspect.Parameter("duplicate_param", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    with pytest.raises(SignatureBuildError) as exc_info:
        validate_accept_double(param, accept_double=False)

    # Verify metadata
    e = exc_info.value
    assert e.error_name == "DUPLICATE PARAMETER ERROR"
    assert e.value == "duplicate_param"
    assert e.value_label == "param.name"
    assert "already defined" in e.problem
    assert e.exception is ValueError


# -----------------------------------------------------------------------------
# Error Content Verification
# -----------------------------------------------------------------------------

def test_error_how_to_fix_contains_contextual_advice():
    """The error message should provide actionable advice on how to fix the duplicate."""
    param = inspect.Parameter("test_name", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    with pytest.raises(SignatureBuildError) as exc_info:
        validate_accept_double(param, accept_double=False)

    how_to_fix = exc_info.value.how_to_fix
    assert any("accept_double=True" in advice for advice in how_to_fix)
    assert any("test_name" in advice for advice in how_to_fix)


def test_error_context_is_correct():
    """Ensure the context field is optional and valid if present."""
    param = inspect.Parameter("x", inspect.Parameter.POSITIONAL_OR_KEYWORD)

    with pytest.raises(SignatureBuildError) as exc_info:
        validate_accept_double(param, accept_double=False)

    exc = exc_info.value

    # Context is optional → must not break anything if missing
    if exc.context:
        assert isinstance(exc.context, str)
        assert exc.context  # not empty