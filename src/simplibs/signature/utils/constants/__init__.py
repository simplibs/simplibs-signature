from .EXCLUDED import EXCLUDED
from .ARGS import ARGS
from .KWARGS import KWARGS


_DESIGN_NOTES = """
# utils/constants

## Contents
Pre-built constants for signature construction — ready to use without
touching the `inspect` module directly.

| Name       | Type                    | Description                                      |
|------------|-------------------------|--------------------------------------------------|
| `EXCLUDED` | `frozenset[str]`        | Default exclusion set — `{"self", "cls"}`        |
| `ARGS`     | `inspect.Parameter`     | Pre-built `*args` parameter (VAR_POSITIONAL)     |
| `KWARGS`   | `inspect.Parameter`     | Pre-built `**kwargs` parameter (VAR_KEYWORD)     |
"""