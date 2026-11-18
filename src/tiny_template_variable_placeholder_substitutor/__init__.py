"""Public API for the tiny template variable placeholder substitutor.

Only :func:`substitute` and :class:`MissingKeysError` are exported; the
implementation lives in :mod:`core` so the package surface stays small.
"""

from .core import MissingKeysError, substitute

__all__ = ["substitute", "MissingKeysError"]
