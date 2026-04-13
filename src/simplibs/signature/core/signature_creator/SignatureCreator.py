import inspect
from typing import Callable, Any, Iterable
from simplibs.sentinels import UNSET
# Outers
from ..parameter_collector import ParameterCollector
from ..utils import compose_signature
from ..validators import validate_param_sources, validate_excluded_names, validate_is_bool
# Inners
from ._mixins import ProcessReturnSourceMixin, ProcessParamSourcesMixin


class SignatureCreator(
    ProcessParamSourcesMixin,      # _process_param_sources(self, param_sources: tuple[inspect.Parameter | Callable, ...], return_source: Any) -> None:
    ProcessReturnSourceMixin,      # _process_return_source(self, return_source: Any) -> None:
):
    """
    A high-level orchestrator for building complex inspect.Signature objects.

    Allows merging multiple sources (Parameter objects or existing Callables)
    into a single signature, providing fine-grained control over parameter
    filtering, deduplication, and return type extraction.
    """

    # Attributes with precise type annotations
    _params_collector: ParameterCollector
    _return_annotation: Any
    _signature: inspect.Signature

    @property
    def signature(self) -> inspect.Signature:
        """The final assembled inspect.Signature."""
        return self._signature

    def __init__(
        self,
        *param_sources: inspect.Parameter | Callable,
        return_source: Any = UNSET,
        excluded_names: Iterable[str] = (),
        accept_double: bool = True,
        replace_double: bool = True,
        include_variadic: bool = True,
        include_binding: bool = True,
        flat_to_kwargs: bool = False,
        validate: bool = True
    ):
        """
        Initializes the SignatureCreator and orchestrates the assembly process.

        Args:
            *param_sources:    Variadic sources (Parameters or Callables) to extract parameters from.
            return_source:     Source for return annotation (Type, Callable, or UNSET).
            excluded_names:    An iterable of parameter names to skip during collection.
            accept_double:     If False, duplicate names raise SignatureBuildError.
            replace_double:    If True, later parameters overwrite earlier ones with the same name.
            include_variadic:  If False, filters out *args and **kwargs.
            include_binding:   If False, filters out 'self' and 'cls'.
            flat_to_kwargs:    If True, transforms all parameters into KEYWORD_ONLY.
            validate:          If True, performs initial input validation and sanitization.

        Raises:
            SignatureBuildError(ValueError):  If param_sources is empty.
            SignatureBuildError(TypeError):   If any param_source is of an invalid type.
            SignatureParameterError(TypeError): If configuration arguments are invalid.
        """

        # 1. Validations and Sanitization
        if validate:
            validate_param_sources(param_sources)
            # Sanitizing excluded_names into a stable tuple via our updated validator
            excluded_names = validate_excluded_names(excluded_names)
            validate_is_bool(accept_double, "accept_double")
            validate_is_bool(replace_double, "replace_double")
            validate_is_bool(include_variadic, "include_variadic")
            validate_is_bool(include_binding, "include_binding")
            validate_is_bool(flat_to_kwargs, "flat_to_kwargs")

        # 2. Initialize the return annotation sentinel
        self._return_annotation = UNSET

        # 3. Initialize the parameter collector with configuration
        self._params_collector = ParameterCollector(
            excluded_names=excluded_names,
            accept_double=accept_double,
            replace_double=replace_double,
            include_variadic=include_variadic,
            include_binding=include_binding,
            flat_to_kwargs=flat_to_kwargs,
            validate=False  # Arguments already validated/sanitized in step 1
        )

        # 4. Process all parameter sources
        # This step may also capture return_annotation as a side effect (optimization).
        self._process_param_sources(param_sources, return_source)

        # 5. Process return annotation
        # If not already set during parameter processing, resolve it explicitly.
        if self._return_annotation is UNSET:
            self._process_return_source(return_source)

        # 6. Compose the final signature
        self._signature = compose_signature(
            parameters=self._params_collector.get_ordered_params(),
            return_annotation=self._return_annotation,
            validate=False  # All components were validated during processing
        )


_DESIGN_NOTES = """
# SignatureCreator

## Purpose
The `SignatureCreator` is the most flexible tool in the library for building
complex `inspect.Signature` objects. It solves the "Signature Merging" problem —
where you want to construct a signature by combining pieces from existing
functions with custom-defined parameters.

## Input Flexibility (Iterable Support)
Following the library-wide standard, `excluded_names` now accepts any `Iterable[str]`. 
This allows users to provide lists, sets, or generator expressions. The input 
is sanitized into a `tuple` during the validation phase to ensure stability 
within the `ParameterCollector`.

## Architecture: The Mixin Strategy (Decomposed Logic Pattern)
The class uses two focused mixins to separate concerns:
1. **ProcessParamSourcesMixin**: Handles iteration over `*param_sources`.
2. **ProcessReturnSourceMixin**: Handles return type resolution.

## The ParameterCollector Integration
The `SignatureCreator` delegates all parameter management (ordering, 
deduplication, and filtering) to `ParameterCollector`.

## Processing Pipeline (Step by Step)
1. **Validate and Sanitize inputs** — Ensure types are correct and materialize iterables.
2. **Initialize return annotation** — Start with `UNSET`.
3. **Initialize collector** — Pass sanitized exclusion list and duplicate rules.
4. **Process param sources** — Route each source to the collector via Mixin.
5. **Process return source** — Resolve return type via Mixin.
6. **Compose signature** — Build the final `inspect.Signature` using `compose_signature`.

## Using the UNSET Sentinel
Standard `None` can be a valid return annotation. `UNSET` allows distinguishing 
between "No annotation provided" and "Explicitly set to None".

## Why validate=False in Internal Calls?
Performance optimization. By the time internal components (Collector, Compose) 
are called, the inputs have already been strictly validated at the entry point.

## Notes
- The resulting `signature` property is read-only and immutable.
- Parameter order is always valid Python order, guaranteed by the Collector.
"""