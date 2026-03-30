import inspect
from typing import Callable
from simplibs.sentinels import UNSET, UnsetType
# Commons
from ..utils import validate_is_bool, validate_is_callable
from ..parameter_collector import ParameterCollector
# Inners
from ._mixins import ProcessFuncMixin, ProcessSourcesMixin, ProcessParametersMixin, ResolveReturnTypeMixin
from ._validations import validate_is_type_or_callable, validate_if_sources_or_base_func_is_set


class SignatureCreator(
    ProcessFuncMixin,        # def _process_func(self, func: Callable, is_base_func: bool = False) -> None
    ProcessSourcesMixin,        # def _process_sources(self) -> None
    ProcessParametersMixin,  # def _process_parameters(self) -> None
    ResolveReturnTypeMixin,  # def _resolve_return_type(self) -> None
):
    """
    Assembles an inspect.Signature from the provided functions, parameters,
    and their combinations.

    Accepts any combination of `sources` and `base_func`, processes their
    parameters and return type, and exposes the result via the `signature`
    property.
    """

    # Attributes
    _sources:         tuple[inspect.Parameter | Callable, ...]
    _base_func:       Callable | None
    _base_func_first: bool
    _return_type:     type | Callable | None | UnsetType
    _param_list:      ParameterCollector
    _signature:       inspect.Signature

    @property
    def signature(self) -> inspect.Signature:
        """The assembled signature."""
        return self._signature


    def __init__(
        self,
        *sources: inspect.Parameter | Callable,
        excluded_names: tuple[str, ...] = None,
        return_type: type | Callable | None | UnsetType = UNSET,
        base_func: Callable | None = None,
        base_func_first: bool = True,
        accept_double: bool = True,
    ):
        """
        Args:
            *sources:           Parameters or functions to add to the signature.
            excluded_names:  Parameter names to exclude from the signature.
            return_type:     The return type of the signature. If not provided
                             and `base_func` is given, its return type is used.
                             May also be a callable — its return annotation is
                             then extracted.
            base_func:       The base function whose parameters and return type
                             serve as the starting point.
            base_func_first: If True, `base_func` parameters come before `sources`.
            accept_double:   If True, duplicate parameter names are silently skipped.

        Raises:
            SignatureBuildError(ValueError): If neither `base_func` nor any
                                             `sources` were provided.
        """

        # 1. Validate that at least one parameter source is provided
        validate_if_sources_or_base_func_is_set(sources, base_func)

        # 2. Store sources
        self._sources = sources

        # 3. Validate and store base_func
        if base_func is not None:
            validate_is_callable(base_func, "base_func")
        self._base_func = base_func

        # 4. Validate and store base_func_first
        validate_is_bool(base_func_first, "base_func_first")
        self._base_func_first = base_func_first

        # 5. Validate and store return_type
        if return_type not in (None, UNSET):
            # Return type priority rules:
            # 1) If return_type is explicitly provided → it has absolute priority.
            # 2) If not provided and base_func is given → base_func return type is used.
            # 3) If neither return_type nor base_func → inspect.Signature.empty is used.
            validate_is_type_or_callable(return_type, "return_type")
        self._return_type = return_type

        # 6. Initialise the parameter collector
        self._param_list = ParameterCollector(excluded_names, accept_double)

        # 7. Assemble the signature
        self._calculate_signature()


    def _calculate_signature(self) -> None:
        """Runs the full signature assembly and stores the result in `_signature`."""

        # 1. Process parameters
        self._process_parameters()

        # 2. Resolve the return type
        self._resolve_return_type()

        # 3. Assemble the final signature
        self._signature = inspect.Signature(
            parameters            = self._param_list.get_ordered(),
            return_annotation     = self._return_type,
            __validate_parameters__ = False,  # CPython internal — skips validation (parameters are already validated)
        )


_DESIGN_NOTES = """
# SignatureCreator

## Purpose
The core class of the library — assembles a complete `inspect.Signature`
from any combination of callables and `inspect.Parameter` instances.
A builder: instantiate it, read the `signature` property, discard the instance.

## Typical usage
```python
sig = SignatureCreator(my_func, my_param, base_func=other_func).signature
```

## Class composition
`SignatureCreator` is assembled from four mixins, each with a single
responsibility:

| Mixin                    | Provides                                              |
|--------------------------|-------------------------------------------------------|
| `ProcessFuncMixin`       | `_process_func()` — extracts parameters from a callable and optionally resolves return type |
| `ProcessSourcesMixin`       | `_process_sources()` — iterates over `sources`, routes each item to the correct handler |
| `ProcessParametersMixin` | `_process_parameters()` — orchestrates processing order based on `base_func_first` |
| `ResolveReturnTypeMixin` | `_resolve_return_type()` — finalises `_return_type` into a form `inspect.Signature` accepts |

## Attributes
| Attribute          | Description                                                        |
|--------------------|--------------------------------------------------------------------|
| `_sources`            | Tuple of user-provided parameter sources                           |
| `_base_func`       | The base callable, or `None`                                       |
| `_base_func_first` | Controls merge order of `base_func` and `sources` parameters          |
| `_return_type`     | Return type in its current state — mutated during assembly         |
| `_param_list`      | `ParameterCollector` instance — stores and orders parameters       |
| `_signature`       | The assembled `inspect.Signature` — set by `_calculate_signature()`|

## Assembly flow in __init__
    1. Validate that at least one parameter source exists.
    2. Store sources.
    3. Validate and store base_func.
    4. Validate and store base_func_first.
    5. Validate and store return_type.
    6. Initialise ParameterCollector with excluded_names and accept_double.
    7. Run _calculate_signature().

## Assembly flow in _calculate_signature
    1. _process_parameters() — fills _param_list via the processing mixins.
    2. _resolve_return_type() — converts _return_type to its final form.
    3. inspect.Signature() — assembles the final signature object.

## return_type priority rules
    1. Explicitly provided → absolute priority, used as-is (after validation).
    2. Not provided + base_func given → base_func return annotation is inherited.
    3. Neither provided → inspect.Signature.empty (no return annotation).

## Why __validate_parameters__=False
`inspect.Signature` performs its own parameter order validation by default.
All parameters have already been validated and ordered correctly by
`ParameterCollector` — re-validating would be redundant and would add
unnecessary overhead on every instantiation.

## Why no __str__ or __repr__
`SignatureCreator` is a builder — its instance is never stored or passed
around. The only output that matters is the `signature` property. Adding
`__str__` or `__repr__` would be superfluous.
"""