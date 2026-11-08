from .apply_signature_to_wraps import apply_signature_to_wraps
from .create_signature_decorator import create_signature_decorator


_DESIGN_NOTES = """
# Decorator Builders Sub-Package

## Purpose
The two pieces the decorators are made of. Plain imports, no `__all__`: the
package root decides what is public.

## Internal Components Registry

| Component                   | Type     | Description                                           |
| :-------------------------- | :------- | :---------------------------------------------------- |
| `apply_signature_to_wraps`  | Function | A transparent wrapper that reports a given signature. |
| `create_signature_decorator`| Function | A decorator that applies a fixed signature.           |
"""
