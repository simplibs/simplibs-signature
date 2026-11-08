import inspect

from simplibs.signature.collector._constants.kinds import (
    KEYWORD_ONLY,
    POSITIONAL_OR_KEYWORD,
    VAR_KEYWORD,
    VAR_POSITIONAL,
)


def test_is_the_inspect_kind():
    assert KEYWORD_ONLY is inspect.Parameter.KEYWORD_ONLY


def test_comes_after_args_and_before_kwargs():
    assert VAR_POSITIONAL < KEYWORD_ONLY < VAR_KEYWORD
    assert POSITIONAL_OR_KEYWORD < KEYWORD_ONLY
