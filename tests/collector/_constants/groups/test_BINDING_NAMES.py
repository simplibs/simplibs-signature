import pytest

from simplibs.signature.collector._constants.groups import BINDING_NAMES


def test_names():
    assert BINDING_NAMES == {"self", "cls"}


def test_is_a_frozenset():
    assert isinstance(BINDING_NAMES, frozenset)


def test_is_read_only():
    with pytest.raises(AttributeError):
        BINDING_NAMES.add("other")
