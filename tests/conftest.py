import inspect

import pytest

from simplibs.signature.collector._constants.kinds import (
    KEYWORD_ONLY,
    POSITIONAL_ONLY,
    POSITIONAL_OR_KEYWORD,
    VAR_KEYWORD,
    VAR_POSITIONAL,
)
from simplibs.signature.collector._constants.strings import CONTAIN_DEFAULT, WITHOUT_DEFAULT


@pytest.fixture
def make_param():
    """A factory of `inspect.Parameter`; the kind is an ordinary parameter by default."""

    def make(
        name,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        default=inspect.Parameter.empty,
        annotation=inspect.Parameter.empty,
    ):
        return inspect.Parameter(name, kind, default=default, annotation=annotation)

    return make


@pytest.fixture
def storage():
    """A fresh `(seen_names, params_map)`, exactly as a collector builds them."""
    params_map = {
        kind: {WITHOUT_DEFAULT: [], CONTAIN_DEFAULT: []}
        for kind in (POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, VAR_POSITIONAL, KEYWORD_ONLY, VAR_KEYWORD)
    }
    return {}, params_map


@pytest.fixture
def names_of():
    """A function that turns parameters (or a signature) into their names."""

    def names(source):
        params = source.parameters.values() if isinstance(source, inspect.Signature) else source
        return [p.name for p in params]

    return names
