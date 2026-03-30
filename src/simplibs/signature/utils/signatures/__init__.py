from .get_signature import get_signature
from .set_signature import set_signature
from .create_copy_signature import create_copy_signature


_DESIGN_NOTES = """
# utils/signatures

## Contents
Low-level utilities for reading, writing, and copying `inspect.Signature` objects.

| Name                   | Description                                                        |
|------------------------|--------------------------------------------------------------------|
| `get_signature`        | Safely retrieves an `inspect.Signature` from a callable            |
| `set_signature`        | Assigns an `inspect.Signature` directly to a function              |
| `create_copy_signature`| Creates a modified copy of a signature from a callable             |
"""