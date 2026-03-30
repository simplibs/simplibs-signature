"""
Tests for EXCLUDED — type, content, immutability, and membership of the default exclusion set.
"""
from simplibs.signature.utils.constants.EXCLUDED import EXCLUDED


# -----------------------------------------------------------------------------
# Type
# -----------------------------------------------------------------------------

def test_excluded_is_frozenset():
    """EXCLUDED must be a frozenset."""
    assert isinstance(EXCLUDED, frozenset)


# -----------------------------------------------------------------------------
# Content
# -----------------------------------------------------------------------------

def test_excluded_contains_self():
    """EXCLUDED must contain 'self'."""
    assert "self" in EXCLUDED


def test_excluded_contains_cls():
    """EXCLUDED must contain 'cls'."""
    assert "cls" in EXCLUDED


def test_excluded_contains_exactly_two_items():
    """EXCLUDED must contain exactly two items — 'self' and 'cls'."""
    assert len(EXCLUDED) == 2


# -----------------------------------------------------------------------------
# Immutability
# -----------------------------------------------------------------------------

def test_excluded_is_immutable():
    """EXCLUDED must be immutable — add() must not be available."""
    assert not hasattr(EXCLUDED, "add")