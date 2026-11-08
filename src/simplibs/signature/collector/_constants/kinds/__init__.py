from .EMPTY import EMPTY
from .KEYWORD_ONLY import KEYWORD_ONLY
from .POSITIONAL_ONLY import POSITIONAL_ONLY
from .POSITIONAL_OR_KEYWORD import POSITIONAL_OR_KEYWORD
from .VAR_KEYWORD import VAR_KEYWORD
from .VAR_POSITIONAL import VAR_POSITIONAL


_DESIGN_NOTES = """
# Collector Kind Constants Sub-Package

## Purpose
Short names for the five parameter kinds the collector stores, and for the
marker of a missing default. Plain imports, no `__all__`: the package root
decides what is public.

## Internal Components Registry

| Component               | Type     | Description                                         |
| :---------------------- | :------- | :-------------------------------------------------- |
| `EMPTY`                 | Constant | `inspect.Parameter.empty`, "no default / annotation". |
| `KEYWORD_ONLY`          | Constant | Parameters passed by name only.                     |
| `POSITIONAL_ONLY`       | Constant | Parameters passed by position only.                 |
| `POSITIONAL_OR_KEYWORD` | Constant | Ordinary parameters.                                |
| `VAR_KEYWORD`           | Constant | The `**kwargs` kind.                                |
| `VAR_POSITIONAL`        | Constant | The `*args` kind.                                   |
"""
