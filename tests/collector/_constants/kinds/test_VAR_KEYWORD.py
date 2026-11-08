import inspect

from simplibs.signature.collector._constants.kinds import KEYWORD_ONLY, VAR_KEYWORD


def test_is_the_inspect_kind():
    assert VAR_KEYWORD is inspect.Parameter.VAR_KEYWORD


def test_comes_last():
    assert KEYWORD_ONLY < VAR_KEYWORD
