"""Core substitution logic for ``${name}`` and ``{{name}}`` placeholders.

Design choice: a single pass with a regex alternation.  This keeps the
substitutor linear in the length of the input and avoids the quoting and
re-scanning problems that come with chained ``str.replace`` calls.  When a
key is missing we collect *all* missing keys before raising so the caller can
fix the whole template in one edit.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Mapping


class MissingKeysError(KeyError):
    """Raised when one or more placeholders have no matching key.

    Subclasses :class:`KeyError` so existing ``except KeyError`` handlers
    keep working, but the message is a plain sentence rather than a repr.
    """

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(self._message())

    def _message(self) -> str:
        shown = ", ".join(repr(k) for k in self.missing)
        return f"missing key(s): {shown}"

    def __str__(self) -> str:  # KeyError would otherwise repr() the message
        return self._message()


# ``\$\{(?P<dollar>[A-Za-z_][A-Za-z0-9_]*)\}`` matches ``${name}`` and
# ``\{\{(?P<brace>[A-Za-z_][A-Za-z0-9_]*)\}\}`` matches ``{{name}}``.
# Names are restricted to Python-style identifiers so that stray braces in
# prose (``{ not a placeholder }``) are left alone.
_PLACEHOLDER = re.compile(
    r"\$\{(?P<dollar>[A-Za-z_][A-Za-z0-9_]*)\}"
    r"|" r"\{\{(?P<brace>[A-Za-z_][A-Za-z0-9_]*)\}\}"
)


def substitute(template: str, values: Mapping[str, Any]) -> str:
    """Return *template* with ``${name}`` and ``{{name}}`` replaced.

    Values are converted with :func:`str`; ``None`` becomes ``"None"``.
    If any placeholder name is absent from *values* a
    :class:`MissingKeysError` is raised listing every missing name in the
    order it first appears in *template*.
    """
    missing: list[str] = []
    seen: Dict[str, None] = {}

    def replace(match: re.Match[str]) -> str:
        name = match.group("dollar") or match.group("brace")
        if name not in values:
            if name not in seen:
                seen[name] = None
                missing.append(name)
            # Returning the original text keeps the error message useful
            # even if the caller ignores the exception.
            return match.group(0)
        return str(values[name])

    result = _PLACEHOLDER.sub(replace, template)
    if missing:
        raise MissingKeysError(missing)
    return result
