import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from jsonschema.exceptions import ValidationError

import check_registry
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


class RegistryPackagePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for filename in (
            "server.official.json", "registry/server.json", "server.json",
            "pyproject.toml", "README.md",
        ):
            target = self.root / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(check_registry.ROOT / filename, target)
        self.manifest = json.loads((self.root / "server.official.json").read_text())
        self.published = {
            "info": {
                "version": self.manifest["version"],
                "description": f"mcp-name: {check_registry.NAME}",
            },
            "urls": [{"yanked": False}],
        }
        self.package_error = None
        self.registry_error = None
        self.schema = {"type": "object"}
        self.output = io.StringIO()
        self.requests = []

    def response(self, url):
        self.requests.append(url)
        if url == check_registry.SCHEMA:
            return self.schema
        if url.startswith("https://pypi.org/"):
            if self.package_error:
                raise self.package_error
            return self.published
        if self.registry_error:
            raise self.registry_error
        return {"server": self.manifest}

    def run_check(self, event="pull_request", allow=False, published=False):
        with (
            patch.object(check_registry, "ROOT", self.root),
            patch.object(check_registry, "get_json", side_effect=self.response),
            patch.dict(os.environ, {"GITHUB_EVENT_NAME": event}, clear=True),
            contextlib.redirect_stdout(self.output),
        ):
            check_registry.check(published, allow)

    def missing_package(self):
        self.package_error = HTTPError("https://pypi.org/fixture", 404, "Not found", {}, None)

    def test_published_package_remains_required_by_default(self):
        self.missing_package()
        for event in ("pull_request", "release", "workflow_dispatch", ""):
            with self.subTest(event=event), self.assertRaises(HTTPError):
                self.run_check(event=event)

    def test_explicit_pull_request_flag_allows_only_missing_package(self):
        self.missing_package()
        self.run_check(allow=True)
        self.assertEqual(len(self.requests), 3)
        self.assertIn("README ownership", self.output.getvalue())
        self.assertIn("unpublished", self.output.getvalue())
        self.assertNotIn("Published PyPI package and ownership verified", self.output.getvalue())

    def test_flag_is_rejected_outside_pull_request_even_if_package_exists(self):
        for event in ("release", "workflow_dispatch", "push", "pull_request_target", ""):
            with self.subTest(event=event), self.assertRaises(ValueError):
                self.run_check(event=event, allow=True)
        self.assertEqual(self.requests, [])

    def test_published_verification_cannot_use_preflight_exception(self):
        with self.assertRaises(ValueError):
            self.run_check(allow=True, published=True)
        self.assertEqual(self.requests, [])

    def test_auth_and_server_errors_are_never_ignored(self):
        for code in (401, 403, 429, 500, 503):
            self.package_error = HTTPError("https://pypi.org/fixture", code, "Failure", {}, None)
            for allow in (False, True):
                with self.subTest(code=code, allow=allow), self.assertRaises(HTTPError):
                    self.run_check(allow=allow)

    def test_network_and_decode_errors_are_not_unpublished_versions(self):
        for error in (URLError("network unavailable"), TimeoutError(), ValueError("invalid JSON")):
            self.package_error = error
            with self.subTest(error=type(error).__name__), self.assertRaises(type(error)):
                self.run_check(allow=True)

    def test_null_payload_is_not_an_unpublished_version(self):
        self.published = None
        with self.assertRaises(TypeError):
            self.run_check(allow=True)

    def test_manifest_parity_still_fails_with_unpublished_exception(self):
        self.missing_package()
        (self.root / "registry/server.json").write_text("{}")
        with self.assertRaisesRegex(AssertionError, "Registry copies differ"):
            self.run_check(allow=True)
        self.assertEqual(self.requests, [check_registry.SCHEMA])

    def test_schema_still_fails_with_unpublished_exception(self):
        self.missing_package()
        self.schema = {"type": "object", "required": ["missing_fixture_field"]}
        with self.assertRaises(ValidationError):
            self.run_check(allow=True)
        self.assertEqual(self.requests, [check_registry.SCHEMA])

    def test_readme_ownership_is_required_before_unpublished_exception(self):
        self.missing_package()
        (self.root / "README.md").write_text("Missing marker")
        with self.assertRaisesRegex(AssertionError, "README ownership marker missing"):
            self.run_check(allow=True)
        self.assertEqual(self.requests, [check_registry.SCHEMA])

    def test_published_ownership_is_still_checked_for_pull_requests(self):
        self.published["info"]["description"] = "Missing marker"
        with self.assertRaisesRegex(AssertionError, "PyPI ownership marker missing"):
            self.run_check(allow=True)

    def test_yanked_package_is_still_rejected_for_pull_requests(self):
        self.published["urls"][0]["yanked"] = True
        with self.assertRaises(AssertionError):
            self.run_check(allow=True)

    def test_registry_errors_are_not_hidden_by_package_exception(self):
        self.missing_package()
        self.registry_error = HTTPError("https://registry.modelcontextprotocol.io/fixture", 403, "Failure", {}, None)
        with self.assertRaises(HTTPError):
            self.run_check(allow=True)

    def test_strict_release_and_dispatch_validate_published_package(self):
        for event in ("release", "workflow_dispatch"):
            with self.subTest(event=event):
                self.run_check(event=event, published=True)
        self.assertIn("Published PyPI package and ownership verified", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
