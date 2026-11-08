import inspect

from simplibs.signature.collector._constants.kinds import (
    KEYWORD_ONLY,
    POSITIONAL_OR_KEYWORD,
    VAR_POSITIONAL,
)


def test_is_the_inspect_kind():
    assert VAR_POSITIONAL is inspect.Parameter.VAR_POSITIONAL


def test_comes_after_ordinary_parameters_and_before_keyword_only():
    assert POSITIONAL_OR_KEYWORD < VAR_POSITIONAL < KEYWORD_ONLY
