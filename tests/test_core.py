import unittest

from tiny_template_variable_placeholder_substitutor import MissingKeysError, substitute


class SubstituteTests(unittest.TestCase):
    def test_dollar_placeholder(self):
        self.assertEqual(substitute("hello ${name}", {"name": "world"}), "hello world")

    def test_brace_placeholder(self):
        self.assertEqual(substitute("hello {{name}}", {"name": "world"}), "hello world")

    def test_mixed_placeholders(self):
        template = "${greeting}, {{name}}!"
        values = {"greeting": "Hi", "name": "Ada"}
        self.assertEqual(substitute(template, values), "Hi, Ada!")

    def test_repeated_placeholder(self):
        self.assertEqual(
            substitute("${x} ${x} {{x}}", {"x": "1"}),
            "1 1 1",
        )

    def test_values_are_stringified(self):
        self.assertEqual(substitute("n=${n}", {"n": 42}), "n=42")
        self.assertEqual(substitute("v=${v}", {"v": None}), "v=None")

    def test_no_placeholders_returns_input(self):
        self.assertEqual(substitute("plain text", {}), "plain text")

    def test_empty_template(self):
        self.assertEqual(substitute("", {}), "")

    def test_stray_braces_are_left_alone(self):
        self.assertEqual(substitute("a { b } c", {}), "a { b } c")
        self.assertEqual(substitute("a ${} c", {}), "a ${} c")
        self.assertEqual(substitute("a {{}} c", {}), "a {{}} c")

    def test_names_must_be_identifiers(self):
        # ``${1x}`` and ``{{x-y}}`` are not valid placeholder names.
        self.assertEqual(substitute("${1x} {{x-y}}", {}), "${1x} {{x-y}}")

    def test_missing_key_raises(self):
        with self.assertRaises(MissingKeysError) as ctx:
            substitute("${a} ${b}", {"a": "1"})
        self.assertEqual(ctx.exception.missing, ["b"])
        self.assertIn("'b'", str(ctx.exception))

    def test_multiple_missing_keys_listed_once_in_order(self):
        with self.assertRaises(MissingKeysError) as ctx:
            substitute("${a} {{b}} ${a} {{c}}", {})
        self.assertEqual(ctx.exception.missing, ["a", "b", "c"])
        message = str(ctx.exception)
        self.assertIn("'a'", message)
        self.assertIn("'b'", message)
        self.assertIn("'c'", message)

    def test_missing_key_error_is_key_error(self):
        with self.assertRaises(KeyError):
            substitute("${a}", {})

    def test_values_may_be_any_mapping(self):
        from collections import OrderedDict

        values = OrderedDict([("a", "1"), ("b", "2")])
        self.assertEqual(substitute("${a}-${b}", values), "1-2")


if __name__ == "__main__":
    unittest.main()
