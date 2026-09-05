import unittest

from check_registry import normalize_optional_fields


class RegistrySerializationTests(unittest.TestCase):
    def test_optional_nested_input_matches_omitted_default(self):
        expected = {"headers": [{"name": "Authorization", "isRequired": False, "isSecret": True}]}
        actual = {"headers": [{"name": "Authorization", "isSecret": True}]}
        self.assertEqual(normalize_optional_fields(expected), actual)
        self.assertIn("isRequired", expected["headers"][0])

    def test_required_input_is_not_equivalent_to_optional(self):
        self.assertNotEqual(normalize_optional_fields({"isRequired": True}), {})

    def test_secret_and_transport_changes_remain_differences(self):
        self.assertNotEqual(normalize_optional_fields({"isSecret": False}), {})
        self.assertNotEqual(normalize_optional_fields({"type": "stdio"}), {"type": "streamable-http"})

    def test_invalid_default_values_are_not_hidden(self):
        for value in (None, 0, "false"):
            self.assertNotEqual(normalize_optional_fields({"isRequired": value}), {})


if __name__ == "__main__":
    unittest.main()
