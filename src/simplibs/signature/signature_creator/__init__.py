from .SignatureCreator import SignatureCreator
from .create_signature import create_signature


_DESIGN_NOTES = """
# signature_creator

## Contents
The core signature assembly engine — available in both class and functional form.

| Name               | Description                                                              |
|--------------------|--------------------------------------------------------------------------|
| `SignatureCreator` | Builder class — assembles an `inspect.Signature` from any combination of callables and parameters |
| `create_signature` | Functional interface — accepts identical parameters, returns the signature directly |

## Usage
```python
# Builder form
sig = SignatureCreator(my_param, base_func=my_func).signature

# Functional form
sig = create_signature(my_param, base_func=my_func)
```
"""