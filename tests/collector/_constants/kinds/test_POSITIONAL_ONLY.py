import inspect

from simplibs.signature.collector._constants.kinds import POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD


def test_is_the_inspect_kind():
    assert POSITIONAL_ONLY is inspect.Parameter.POSITIONAL_ONLY


def test_comes_first():
    assert POSITIONAL_ONLY < POSITIONAL_OR_KEYWORD
