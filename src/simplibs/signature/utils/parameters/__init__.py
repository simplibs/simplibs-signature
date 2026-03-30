from .create_positional_parameter import create_positional_parameter
from .create_keyword_parameter import create_keyword_parameter


_DESIGN_NOTES = """
# utils/parameters

## Contents
Convenience factories for creating `inspect.Parameter` instances without
touching the `inspect` module directly.

| Name                         | Description                                               |
|------------------------------|-----------------------------------------------------------|
| `create_positional_parameter`| Creates a `POSITIONAL_ONLY` or `POSITIONAL_OR_KEYWORD` parameter |
| `create_keyword_parameter`   | Creates a `KEYWORD_ONLY` parameter                        |
"""