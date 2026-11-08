import inspect

from simplibs.signature.collector._constants.kinds import (
    POSITIONAL_ONLY,
    POSITIONAL_OR_KEYWORD,
    VAR_POSITIONAL,
)


def test_is_the_inspect_kind():
    assert POSITIONAL_OR_KEYWORD is inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_comes_between_positional_only_and_args():
    assert POSITIONAL_ONLY < POSITIONAL_OR_KEYWORD < VAR_POSITIONAL
