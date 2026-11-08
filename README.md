# ✒️ `simplibs-signature`

[![PyPI](https://img.shields.io/pypi/v/simplibs-signature)](https://pypi.org/project/simplibs-signature/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](https://github.com/simplibs/simplibs-signature/blob/main/LICENSE)
[![tests](https://github.com/simplibs/simplibs-signature/actions/workflows/tests.yml/badge.svg)](https://github.com/simplibs/simplibs-signature/actions)

**Say what a wrapper really accepts — and let tools believe it.**

A Python library for building, copying and changing the **signature** of a function. A wrapper that
takes `(*args, **kwargs)` hides everything from your editor, from `help()` and from documentation
generators; this library gives it the signature it *really* has — copied from the function it wraps,
assembled from parameters and other functions, or written by hand — and keeps it **valid**: the
parameters always end up in the order Python requires, a name is never there twice, and a second
`*args` can never sneak in. A wrong call is a structured card that says what and how to fix it.

```python
import inspect
from simplibs.signature import signature_copy

def original(a: int, b: str = "x", *args, **kwargs) -> bool: ...

@signature_copy(original, excepts=["b"])
def wrapper(*args, **kwargs):
    ...

str(inspect.signature(wrapper))     # -> '(a: int, *args, **kwargs) -> bool'
```

> The decorators change only what `inspect` **reports**. They do not check or change how the wrapper
> is called — the call goes through unchanged. The signature describes the call; it does not enforce it.

---

## 🧭 The Core Philosophy

Writing a signature by hand means `inspect.Parameter("x", inspect.Parameter.KEYWORD_ONLY, ...)` four
times over, then finding the right place for each parameter — required before optional, `*args` before
the keyword-only ones, never anything after `**kwargs` — and `inspect.Signature` itself checks
surprisingly little: it accepts `(*a, *b)` without a word. `simplibs-signature` takes the chore over:

* **A signature is built, not patched.** Every parameter goes through one **collector** that keeps
  the order valid whatever the order you add them in. You say *what* goes in, never *where*.
* **Sources in, priority by order.** A source is an `inspect.Parameter` or any callable (all its
  parameters are taken). Sources are merged in the order given, and with the default settings the
  **later one wins** a name collision — so the order of your arguments is the priority.
* **One `*args`, one `**kwargs`.** A signature holds one of each. A second one is a collision even
  under another name (`*a` after `*args`) and is settled by the same rules as any duplicate.
* **Nothing is changed behind your back.** The decorators wrap, the modifiers return a new
  signature, the original stays as it was. The one function that changes an object in place says so
  in its name: `set_signature`.
* **Names are filtered by what they are.** `include_variadic=False` leaves out every `*args` and
  `**kwargs` by their *kind*, however they are called; `self` and `cls`, which have no kind of their
  own, are recognised by name.
* **Functions first, decorators on top.** The logic lives in functions you can call on their own;
  the decorators are thin wrappers over them.
* **Every error is a card.** A wrong call is a `ParamError` from
  [`simplibs-exception`](https://pypi.org/project/simplibs-exception/) — what was given, what was
  expected, how to fix it — and it points at **your** code, not at the library's insides.
* **Layers that only look left.** `constants` ← `collector` ← `tools` ← `orchestrators` ←
  `decorators` — every layer imports only from those before it.

```python
create_signature(f, g, accept_double=False)    # -> raises: DUPLICATE PARAMETER ERROR — 'rest' collides with the already defined variadic positional parameter 'args'
create_signature(f, 5)                         # -> raises: ValidationError — a source must be a Parameter or a callable
```

---

## 📦 Installation

```bash
pip install simplibs-signature
```

Requires Python 3.11+. Runtime dependencies: [`simplibs-exception`](https://pypi.org/project/simplibs-exception/)
(the error cards), [`simplibs-validate`](https://pypi.org/project/simplibs-validate/)
(`@validate_call` on every public function) and [`simplibs-sentinels`](https://pypi.org/project/simplibs-sentinels/)
(`UNSET`, the marker of "not given" — `None` is a valid return annotation, so it cannot play that part).

---

## 🚀 Quick Start in 60 Seconds

### Level 1: Give a wrapper the signature it really has

```python
import inspect
from simplibs.signature import signature, signature_copy, signature_set
from simplibs.signature import create_keyword_parameter, create_positional_parameter

def original(a: int, b: str = "x", *args, **kwargs) -> bool: ...

# copy another function's signature, with changes
@signature_copy(original, excepts=["b"])
def wrapper(*args, **kwargs): ...
str(inspect.signature(wrapper))       # -> '(a: int, *args, **kwargs) -> bool'

# start from the function itself and add to it
@signature(create_keyword_parameter("timeout", annotation=float, default=3.0), returns=int)
def fetch(url: str, *, retries: int = 2): ...
str(inspect.signature(fetch))         # -> '(url: str, *, retries: int = 2, timeout: float = 3.0) -> int'

# or attach a finished signature
fixed = inspect.Signature([
    create_positional_parameter("x", annotation=int),
    create_keyword_parameter("verbose", annotation=bool, default=False),
])

@signature_set(fixed)
def anything(*args, **kwargs): ...
str(inspect.signature(anything))      # -> '(x: int, *, verbose: bool = False)'
```

### Level 2: Build a signature from any mix of sources

```python
import inspect
from simplibs.signature import create_signature, copy_signature

def f(a, *args, b=1): ...
def g(c, *rest): ...

create_signature(f, g)                                # -> (a, c, *rest, b=1)      the later *rest replaces *args
create_signature(f, g, replace_double=False)          # -> (a, c, *args, b=1)      the earlier one stays
create_signature(f, g, include_variadic=False)        # -> (a, c, *, b=1)
create_signature(f, g, flat_to_kwargs=True)           # -> (*, a, b=1, c)          everything keyword-only
create_signature(f, return_source=int)                # -> (a, *args, b=1) -> int

copy_signature(g, extra_params=[inspect.Parameter("z", inspect.Parameter.KEYWORD_ONLY)])   # -> (c, *rest, z)
```

### Level 3: Change a signature you already have

```python
import inspect
from simplibs.signature import (
    add_params_to_signature, delete_params_from_signature, replace_return_annotation_in_signature,
    create_keyword_parameter,
)

sig = inspect.signature(original)       # (a: int, b: str = 'x', *args, **kwargs) -> bool

add_params_to_signature(sig, [create_keyword_parameter("dry_run", annotation=bool, default=False)])
# -> (a: int, b: str = 'x', *args, dry_run: bool = False, **kwargs) -> bool

delete_params_from_signature(sig, ["b", "kwargs"])           # -> (a: int, *args) -> bool
replace_return_annotation_in_signature(sig, int)             # -> (a: int, b: str = 'x', *args, **kwargs) -> int
```

### Level 4: The collector, when you want full control

```python
from simplibs.signature import ParameterCollector, compose_signature

collector = ParameterCollector(include_variadic=False)
collector.add_params(inspect.signature(original).parameters.values())

[p.name for p in collector.get_ordered_params()]             # -> ['a', 'b']
compose_signature(collector.get_ordered_params(), int)       # -> (a: int, b: str = 'x') -> int
```

---

## 🛠️ Architecture & Package Structure

```
src/simplibs/signature/
├── constants/            ◄── ARGS, KWARGS — ready-made *args and **kwargs parameters
├── collector/            ◄── ParameterCollector — one valid, ordered set of parameters
├── tools/                ◄── The small building blocks
│   ├── parameters/       ◄── create_keyword_parameter, create_positional_parameter
│   ├── operations/       ◄── get_signature, set_signature, compose_signature
│   └── modifiers/        ◄── add_params_to_signature, delete_params_from_signature, replace_return_annotation_in_signature
├── orchestrators/        ◄── create_signature, copy_signature — the high-level builders
└── decorators/           ◄── signature, signature_copy, signature_set (+ builders)
```

Everything public is importable straight from `simplibs.signature`:

```python
from simplibs.signature import (
    signature, signature_copy, signature_set,        # decorators
    create_signature, copy_signature,                # builders
    ParameterCollector,                              # the collector
    get_signature, set_signature, compose_signature, # operations
    add_params_to_signature, delete_params_from_signature, replace_return_annotation_in_signature,
    create_positional_parameter, create_keyword_parameter,
    apply_signature_to_wraps, create_signature_decorator,
    ARGS, KWARGS,
)
```

### The options every builder shares

The same options mean the same thing in `create_signature`, `copy_signature`, the decorators and — where
they are offered — the modifiers and the collector itself.

| Option             | Default | Meaning                                                                          |
|--------------------|---------|----------------------------------------------------------------------------------|
| `accept_double`    | `True`  | If `False`, a name collision raises a `ParamError`. If `True`, `replace_double` decides. |
| `replace_double`   | `True`  | Who wins a collision: the **later** parameter (`True`) or the **earlier** one (`False`). |
| `include_variadic` | `True`  | If `False`, every `*args` and `**kwargs` is left out, whatever it is called.      |
| `include_binding`  | `True`  | If `False`, parameters named `self` and `cls` are left out.                        |
| `flat_to_kwargs`   | `False` | Everything keyword-only; `*args` dropped, all `**kwargs` merged into one.          |
| `_validate_call`   | `True`  | Reserved switch of `@validate_call`: `False` skips the validation of the arguments. |

Parameters that take several values — `excepts`, `extras`, `excluded_names`, `extra_params`,
`params_to_add`, `parameters` — accept **any iterable**: a list, a tuple, a set or a generator.
Every public function with such a parameter is decorated with
`@validate_call(materialize_iterators=True)` (from `simplibs-validate`), so a generator is read once
and the function receives a tuple that it can read again; its items are still validated. With
`_validate_call=False` nothing is validated or converted, so pass a list or a tuple there.

---

## 🎀 `decorators/` — Give a wrapper its real signature

Three decorators that differ in **where the signature comes from**, and the two builders they are made of.
Each returns a transparent wrapper — sync or async, as the function is — that reports the new signature
to `inspect`, and leaves the original function untouched.

| Name                         | Description / Parameters                                                                                          |
|------------------------------|-------------------------------------------------------------------------------------------------------------------|
| `signature`                  | Assembles the signature from sources and, by default, the function itself (`*params`, `returns`, `excepts`, `use_func`, `func_first`, + shared options). |
| `signature_copy`             | Copies another callable's signature, with changes (`base_func`, `returns`, `extras`, `excepts`, + shared options).  |
| `signature_set`              | Attaches a finished `inspect.Signature` (`signature`).                                                              |
| `create_signature_decorator` | Turns a finished signature into a reusable decorator (`signature`).                                                 |
| `apply_signature_to_wraps`   | Wraps one function in a transparent wrapper with a given signature (`function`, `signature`).                       |

➡️ [README_SIGNATURE_DECORATORS](https://github.com/simplibs/simplibs-signature/blob/main/docs/README_SIGNATURE_DECORATORS.md)

---

## 🎼 `orchestrators/` — Build a whole signature in one call

The high-level builders. They combine the collector with the tools: load the sources, settle the return
annotation, compose and validate the result.

| Function           | Description / Parameters                                                                                              |
|--------------------|-----------------------------------------------------------------------------------------------------------------------|
| `create_signature` | A signature from any mix of parameters and callables (`*param_sources`, `return_source`, `excluded_names`, + shared options). |
| `copy_signature`   | A changed copy of one callable's signature (`function`, `return_annotation`, `extra_params`, `excluded_names`, + shared options). |

➡️ [README_SIGNATURE_ORCHESTRATORS](https://github.com/simplibs/simplibs-signature/blob/main/docs/README_SIGNATURE_ORCHESTRATORS.md)

---

## 🧺 `collector/` — One valid, ordered set of parameters

The engine behind everything above, and a class you can use yourself. It excludes what you do not want,
settles name collisions, keeps the order Python requires and, in flat mode, turns everything into one
keyword-only API.

| Member               | Description / Parameters                                                                                  |
|----------------------|-----------------------------------------------------------------------------------------------------------|
| `ParameterCollector` | The collector (`excluded_names`, `accept_double`, `replace_double`, `include_variadic`, `include_binding`, `flat_to_kwargs`). |
| `add_param`          | Adds one parameter (`param`).                                                                              |
| `add_params`         | Adds several, one after another (`params`).                                                                |
| `get_ordered_params` | Returns the stored parameters in the order Python requires; a tuple.                                       |

➡️ [README_SIGNATURE_PARAMETER_COLLECTOR](https://github.com/simplibs/simplibs-signature/blob/main/docs/README_SIGNATURE_PARAMETER_COLLECTOR.md)

---

## 🔧 `tools/` — The small building blocks

Independent functions: create a parameter, read, build and attach a signature, change a signature. They
know nothing about the orchestrators or the decorators above them.

| Function                                 | Group      | Description / Parameters                                                       |
|------------------------------------------|------------|--------------------------------------------------------------------------------|
| `create_positional_parameter`            | parameters | A positional-only or ordinary parameter (`name`, `annotation`, `default`, `positional_only`). |
| `create_keyword_parameter`               | parameters | A keyword-only parameter (`name`, `annotation`, `default`).                    |
| `get_signature`                          | operations | Reads a signature, with a readable failure (`function`).                       |
| `set_signature`                          | operations | Attaches a signature through `__signature__` — changes the function itself (`function`, `signature`). |
| `compose_signature`                      | operations | Builds an `inspect.Signature` and always checks its structure (`parameters`, `return_annotation`). |
| `add_params_to_signature`                | modifiers  | A copy of a signature with parameters added (`signature`, `params_to_add`, `accept_double`, `replace_double`, `flat_to_kwargs`). |
| `delete_params_from_signature`           | modifiers  | A copy of a signature without the named parameters (`signature`, `excluded_names`). |
| `replace_return_annotation_in_signature` | modifiers  | A copy of a signature with another return annotation (`signature`, `new_return_annotation`). |
| `ARGS`, `KWARGS`                         | constants  | Ready-made `*args` and `**kwargs` parameters.                                    |

➡️ [README_SIGNATURE_TOOLS](https://github.com/simplibs/simplibs-signature/blob/main/docs/README_SIGNATURE_TOOLS.md)

---

## ⚠️ Exceptions

The library defines no exceptions of its own. A wrong call is a structured
[`simplibs.exception`](https://pypi.org/project/simplibs-exception/) `ParamError` card; its `label` names the
offending part and its `value` is what was given. Where a card wraps a standard exception, that type is in
its MRO, so an existing `except ValueError:` keeps working. An argument of the wrong type is a
`ValidationError` raised by `@validate_call` before the function runs.

| Error name                       | Wraps                                 | Raised when                                                              |
|----------------------------------|---------------------------------------|--------------------------------------------------------------------------|
| `DUPLICATE PARAMETER ERROR`      | `ValueError`                          | A name — or a second `*args` / `**kwargs` — collides and `accept_double=False` |
| `INVALID PARAMETER ORDER`        | `SyntaxError`                         | A required positional parameter would follow an optional one              |
| `INVALID PARAMETER KIND ERROR`   | `KeyError`                            | A parameter has a kind the collector cannot store                         |
| `INVALID PARAMETER SOURCE`       | `TypeError`                           | A source of `create_signature` is neither a `Parameter` nor a callable    |
| `INVALID DEFAULT VALUE`          | `TypeError`                           | A default value contradicts a plain-class annotation                      |
| `SIGNATURE INTROSPECTION ERROR`  | `ValueError`, `TypeError`             | `get_signature` cannot read the signature of an object                    |
| `SIGNATURE COMPOSITION ERROR`    | `ValueError`, `AttributeError`, `TypeError` | `compose_signature` gets parameters that do not form a signature     |
| `SIGNATURE STRUCTURE ERROR`      | `ValueError`                          | `add_params_to_signature` produces a structure `inspect` refuses           |
| `SIGNATURE TYPE ERROR`           | `TypeError`                           | `add_params_to_signature` meets a parameter of an unusable type            |

Every card points at **your** call: all `simplibs` frames are left out of the reported location, and only if
nothing else is left does it fall back to the last one. Each helper README ends with the errors of its own package.

---

## 🔗 Related libraries

* **[`simplibs-exception`](https://pypi.org/project/simplibs-exception/)** — the structured exception cards behind every error here.
* **[`simplibs-validate`](https://pypi.org/project/simplibs-validate/)** — `@validate_call`, which checks the arguments of every public function; its reserved `_validate_call` switch is the one these functions share.
* **[`simplibs-sentinels`](https://pypi.org/project/simplibs-sentinels/)** — `UNSET`, the marker of a value that was not given.

---

## ☯️ About simplibs

All libraries in the **simplibs** (Simple Libraries) ecosystem share a common
engineering philosophy:

* **Dyslexia-friendly:**
We actively minimize cognitive load. Code is atomized into small, self-contained units,
files are named directly after the logical task they perform, and explanations describe
*why* something is designed, not just *what* it is.
* **Programmer's Zen:**
Nothing should be missing, and nothing should be superfluous. We value clean execution
paths and robust, understandable code architectures over rushed, messy feature sets.
* **Defensive Style:**
We actively anticipate edge cases and failure modes so that only safe operational paths
remain. Our code is built to degrade gracefully rather than crash unexpectedly.
* **Minimalism:**
Find the most direct path to the goal in as few operational steps as possible without
taking shortcuts on safety, readability, or completeness.
* **Code as Craft:**
Code should be pleasant to look at, readable at a glance, and evoke structural harmony.
We treat software engineering as a precision trade.

---

### 🤝 Contributing & Community

This is an **open-source project** built with love and care. We strongly believe in
community collaboration and welcome any feedback, bug reports, or feature ideas!

* **Want to contribute?** Feel free to open an Issue or submit a Pull Request.
* **Want to get in touch?** If you'd like to discuss the project further, collaborate,
  or just say hello, feel free to open a GitHub Issue or start a Discussion.

---

### 📝 License

This library is released under the **MIT License**. Build great things!

---
