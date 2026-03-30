# simplibs-signature

> Lightweight utilities for dynamic and declarative function signature manipulation.
> Inspect, copy, assemble, and apply `inspect.Signature` objects — with a clean
> API and no magic.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Licence](https://img.shields.io/badge/licence-MIT-green)
![PyPI](https://img.shields.io/pypi/v/simplibs-signature)
```python
# Assemble a signature from multiple sources
sig = create_signature(extra_param, base_func=my_func)

# Or use the decorator shorthand
@signature_from(extra_param, base_func_first=False)
def my_func(*args, **kwargs):
    ...

@signature_copy(MyClass.__init__, return_type=MyClass)
def create(*args, **kwargs):
    ...
```

---

## Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Decorators](#decorators)
- [Signature operations](#signature-operations)
- [Parameter creators](#parameter-creators)
- [SignatureCreator](#signaturecreator)
- [Constants](#constants)
- [About the simplibs ecosystem](#about-the-simplibs-ecosystem)

---

## Installation
```bash
pip install simplibs-signature
```
```python
from simplibs.signature import create_signature, signature_from, signature_copy
```

> Note: This library automatically installs `simplibs-exception` and
> `simplibs-sentinels` as core dependencies.

---

## Quick start

The library is built around `SignatureCreator` — a class that assembles an
`inspect.Signature` from any combination of callables and `inspect.Parameter`
instances. Its direct functional interface is `create_signature`, which accepts
identical parameters and returns the assembled signature without exposing the
builder instance.

On top of that, the library provides a set of utilities for working with
signatures directly — retrieving, copying, applying — and two decorators,
`signature_copy` and `signature_from`, that cover the most common use cases
in a compact one-liner form.

### Assemble a signature programmatically
```python
from simplibs.signature import create_signature, create_keyword_parameter

extra = create_keyword_parameter("timeout", annotation=int, default=30)

sig = create_signature(extra, base_func=my_func)
# → (host: str, port: int, *, timeout: int = 30)
```

### Copy a signature from an existing function
```python
from simplibs.signature import signature_copy

class MyClass:
    def __init__(self, name: str, value: int = 0):
        ...

@signature_copy(MyClass.__init__, return_type=MyClass)
def create(*args, **kwargs):
    return MyClass(*args, **kwargs)

# create now reports: (name: str, value: int = 0, **kwargs) -> MyClass
```

### Merge parameters from multiple sources
```python
from simplibs.signature import signature_from, create_keyword_parameter

extra = create_keyword_parameter("timeout", annotation=int, default=30)

@signature_from(extra)
def connect(host: str, port: int):
    ...

# connect now reports: (host: str, port: int, *, timeout: int = 30)
```

---

## Decorators

The two main decorators — the primary public interface of the library.

### signature_copy

Copies and normalises a signature from an existing callable onto the decorated
function. Always removes `self`/`cls` and appends `**kwargs`.
```python
from simplibs.signature import signature_copy

@signature_copy(base_func, return_type=MyClass)
def my_func(*args, **kwargs):
    ...
```

| Parameter     | Type                            | Description                                                                        |
|---------------|---------------------------------|------------------------------------------------------------------------------------|
| `base_func`   | `Callable`                      | The function or method whose signature is copied                                   |
| `return_type` | `type \| None \| UNSET`         | Override the return annotation. `UNSET` preserves the original, `None` removes it |

### signature_from

Assembles a new signature from the decorated function and any additional
parameter sources. The decorated function becomes `base_func`.
```python
from simplibs.signature import signature_from

@signature_from(param_or_func, ..., base_func_first=True)
def my_func(*args, **kwargs):
    ...
```

| Parameter        | Type                                  | Description                                                                        |
|------------------|---------------------------------------|------------------------------------------------------------------------------------|
| `*sources`       | `inspect.Parameter \| Callable`       | Parameters or callables to merge into the signature                                |
| `excluded_names` | `tuple[str, ...]`                     | Parameter names to exclude                                                         |
| `return_type`    | `type \| Callable \| None \| UNSET`   | Return annotation. If `UNSET` and `base_func` has one, it is inherited             |
| `base_func_first`| `bool`                                | If `True`, decorated function's parameters come first (default: `True`)            |
| `accept_double`  | `bool`                                | If `True`, duplicate parameter names are silently skipped (default: `True`)        |

---

## Signature operations

Lower-level tools for working with `inspect.Signature` objects directly.

### get_signature

Safely retrieves an `inspect.Signature` from any callable. Converts Python's
raw `ValueError` and `TypeError` into structured `SignatureBuildError` instances:
```python
from simplibs.signature import get_signature

sig = get_signature(my_func)
```

### set_signature

Assigns an `inspect.Signature` directly to a function via `__signature__`.
Returns the original function — allows inline assignment:
```python
from simplibs.signature import set_signature

set_signature(my_func, my_signature)
```

### create_copy_signature

Creates a modified copy of a signature from a callable — the lower-level
counterpart to `signature_copy`. Use when you need full control over
normalisation or want the `inspect.Signature` object directly rather than
a decorator:
```python
from simplibs.signature import create_copy_signature
from simplibs.sentinels import UNSET

sig = create_copy_signature(
    MyClass.__init__,
    return_type = MyClass,   # override return annotation
    normalize   = True,      # remove self/cls, append **kwargs (default: True)
)
```

### apply_signature_to_wraps

Creates a new wrapper around a function and assigns a custom signature to it.
The building block for decorators — use when you need a new callable, not just
a modified one:
```python
from simplibs.signature import apply_signature_to_wraps

wrapped = apply_signature_to_wraps(my_func, my_signature)
```

### create_signature_decorator

Produces a reusable decorator from an `inspect.Signature`. Use when the same
signature needs to be applied to multiple functions:
```python
from simplibs.signature import create_signature_decorator

decorator = create_signature_decorator(my_signature)

@decorator
def func_a(*args, **kwargs): ...

@decorator
def func_b(*args, **kwargs): ...
```

---

## Parameter creators

Convenience factories for building `inspect.Parameter` instances without
touching the `inspect` module directly.

### create_positional_parameter
```python
from simplibs.signature import create_positional_parameter

param = create_positional_parameter("name", annotation=str)
param = create_positional_parameter("x", annotation=int, default=0, positional_only=True)
```

### create_keyword_parameter
```python
from simplibs.signature import create_keyword_parameter

param = create_keyword_parameter("timeout", annotation=int, default=30)
```

Both factories accept:

| Parameter         | Type    | Description                                                                        |
|-------------------|---------|------------------------------------------------------------------------------------|
| `name`            | `str`   | Parameter name                                                                     |
| `annotation`      | `type`  | Type annotation — omit for no annotation                                           |
| `default`         | `Any`   | Default value — omit for no default                                                |
| `positional_only` | `bool`  | `create_positional_parameter` only — produces `POSITIONAL_ONLY` if `True`         |

---

## SignatureCreator

The engine behind `signature_from` and `create_signature` — assembles an
`inspect.Signature` from any combination of callables and `inspect.Parameter`
instances. Use it directly when you need the builder instance itself, or reach
for `create_signature` for the one-liner functional form:
```python
from simplibs.signature import SignatureCreator, create_signature

# Builder form — access the instance if needed
creator = SignatureCreator(extra_param, base_func=my_func)
sig = creator.signature

# Functional form — when only the signature is needed
sig = create_signature(extra_param, base_func=my_func)
```

| Parameter        | Type                                  | Description                                                                    |
|------------------|---------------------------------------|--------------------------------------------------------------------------------|
| `*sources`       | `inspect.Parameter \| Callable`       | Parameters or callables to merge in                                            |
| `excluded_names` | `tuple[str, ...]`                     | Parameter names to exclude                                                     |
| `return_type`    | `type \| Callable \| None \| UNSET`   | Return annotation source — type, callable, `None`, or `UNSET`                 |
| `base_func`      | `Callable \| None`                    | Base function — its parameters and return type are the starting point          |
| `base_func_first`| `bool`                                | If `True`, `base_func` parameters come first (default: `True`)                 |
| `accept_double`  | `bool`                                | If `True`, duplicate names are silently skipped (default: `True`)              |

### return_type priority

| Value      | Behaviour                                                        |
|------------|------------------------------------------------------------------|
| a type     | Used directly as the return annotation                           |
| a callable | Its return annotation is extracted and used                      |
| `None`     | Return annotation is removed                                     |
| `UNSET`    | Inherited from `base_func` if available, otherwise empty         |

---

## Constants

Pre-built `inspect.Parameter` instances and a frozenset of default exclusions —
ready to use without touching the `inspect` module:
```python
from simplibs.signature import ARGS, KWARGS, EXCLUDED

# ARGS     — *args     (VAR_POSITIONAL)
# KWARGS   — **kwargs  (VAR_KEYWORD)
# EXCLUDED — frozenset({"self", "cls"})
```

`EXCLUDED` is the default exclusion set used by `ParameterCollector` and
`create_copy_signature` — `self` and `cls` are always skipped automatically.

---

## About the simplibs ecosystem

`simplibs-signature` is part of the **simplibs** ecosystem — a collection of
small, self-contained Python libraries united under a common namespace and
philosophy. The name *simplibs* is short for *simple libraries*.

This library builds on two other simplibs packages:

- **`simplibs-exception`** — a structured exception that communicates with the
  developer: describing not just what went wrong, but pointing towards a fix.
  All errors raised by `simplibs-signature` are structured `SimpleException`
  subclasses, catchable as `SignatureError` or the more specific
  `SignatureParameterError` and `SignatureBuildError`:
```python
from simplibs.signature import SignatureError, SignatureBuildError, SignatureParameterError

try:
    create_signature()  # no sources provided
except SignatureBuildError:
    ...  # signature could not be built

try:
    create_keyword_parameter(name=123)  # wrong type
except SignatureParameterError:
    ...  # invalid argument

try:
    ...
except SignatureError:
    ...  # catches all simplibs-signature errors
```

- **`simplibs-sentinels`** — sentinel values shared across the ecosystem.
  `UNSET` is used throughout `simplibs-signature` to distinguish between
  a parameter that was not provided and one explicitly set to `None`:
```python
from simplibs.sentinels import UNSET
from simplibs.signature import create_copy_signature

sig = create_copy_signature(my_func, return_type=UNSET)  # preserve original
sig = create_copy_signature(my_func, return_type=None)   # remove annotation
```

All libraries in the simplibs ecosystem share a common philosophy:

**Dyslexia-friendly** — minimise mental load. Atomise code into self-contained
units, name files after the logic they contain, write explanations that describe
*why* — not just *what*.

**Programmer's zen** — nothing should be missing and nothing should be
superfluous. The journey is the destination: code should be fully understood;
better to go slowly and correctly than quickly and with mistakes. The
crystallisation approach — not perfection on the first try, but gradual
refinement towards it.

**Defensive style** — anticipate all possible failure modes so that only safe
paths remain. Never raise unexpected errors; degrade gracefully.

**Minimalism** — find the path to the goal in as few steps as possible, but
leave nothing out. Each file has one responsibility.

**Code as craft** — code should be pleasant to look at and evoke a sense of
harmony. Treat code as a small work of art — like a carpenter carving a
sculpture. Optimise for the user: everything should make sense without having
to study the documentation at length.

These are aspirations — a sense of direction. And that is exactly what the
note about the journey becoming the destination is all about. 🙂

---

*The library is covered by unit tests across all modules.
Tests are part of the repository and serve
as living documentation of the expected behaviour.*