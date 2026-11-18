# tiny_template_variable_placeholder_substitutor

Replaces `${name}` and `{{name}}` placeholders in a string using a mapping of
values, and raises a single error that lists every missing key.

```python
from tiny_template_variable_placeholder_substitutor import substitute

substitute("Hello ${name}, you have {{count}} messages", {"name": "Ada", "count": 3})
# 'Hello Ada, you have 3 messages'
```

When a key is missing, `MissingKeysError` (a `KeyError` subclass) is raised
with a `missing` attribute and a readable message:

```python
from tiny_template_variable_placeholder_substitutor import MissingKeysError, substitute

try:
    substitute("${a} ${b}", {"a": "1"})
except MissingKeysError as exc:
    exc.missing  # ['b']
    str(exc)     # "missing key(s): 'b'"
```

## Why this exists

Templates arrive from configuration files and user input, and a plain
`str.format` or `str.replace` loop either chokes on the first missing key or
silently leaves unknown placeholders in place. This library does one pass,
reports every missing key at once, and leaves malformed braces untouched so
that unrelated prose is not mangled. The trade-off is that placeholder names
are restricted to Python-style identifiers (`[A-Za-z_][A-Za-z0-9_]*`);
anything else, such as `${1x}` or `{{x-y}}`, is treated as literal text rather
than a placeholder.

## Edge case to know about

Only the two forms `${name}` and `{{name}}` are recognised. A single-brace
form `{name}` is *not* a placeholder and is returned unchanged. Values are
converted with `str`, so `None` becomes `"None"` and numbers become their
decimal representation.
