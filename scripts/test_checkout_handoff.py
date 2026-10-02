"""Exercise actual checkout source with fake SDK decorators and HTTP transport.

No SDK transport, live backend, account, email or billing action is exercised.
"""

import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import sys
import threading
import types
import unittest
from unittest.mock import patch

import httpx


ROOT = Path(__file__).resolve().parents[1]


class DecoratorOnlyServer:
    def __init__(self, name):
        self.name = name

    def tool(self):
        return lambda function: function

    def resource(self, uri):
        return lambda function: function


def load_server(environment=None):
    modules = {
        name: types.ModuleType(name)
        for name in ("mcp", "mcp.server", "mcp.server.mcpserver")
    }
    modules["mcp.server.mcpserver"].MCPServer = DecoratorOnlyServer
    exceptions = types.ModuleType("mcp.server.mcpserver.exceptions")
    exceptions.ToolError = RuntimeError
    modules[exceptions.__name__] = exceptions
    package_spec = importlib.util.spec_from_file_location(
        "_checkout_fixture", ROOT / "parlayapi_mcp" / "__init__.py",
        submodule_search_locations=[str(ROOT / "parlayapi_mcp")],
    )
    package = importlib.util.module_from_spec(package_spec)
    modules[package_spec.name] = package
    env = {
        "PARLAYAPI_KEY": "", "PARLAY_API_KEY": "",
        "PARLAYAPI_BASE_URL": "https://parlay.example.test",
        **(environment or {}),
    }
    with patch.dict(sys.modules, modules), patch.dict(os.environ, env):
        package_spec.loader.exec_module(package)
        spec = importlib.util.spec_from_file_location(
            "_checkout_fixture.server", ROOT / "parlayapi_mcp" / "server.py",
        )
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
    return server


class CheckoutHandoffTests(unittest.TestCase):
    def setUp(self):
        self.server = load_server()
        self.requests = []
        real_client = httpx.Client

        def respond(request):
            self.requests.append(request)
            self.assertEqual(request.url.host, "parlay.example.test")
            if request.url.path == "/v1/agent/checkout-link":
                email = json.loads(request.content)["email"]
                # This fake backend models the existing ownership boundary.
                # It does not verify that the live backend performs the check.
                owners = {
                    "test-owner-key": "owner@example.test",
                    "test-second-key": "second@example.test",
                }
                key = request.headers.get("X-API-Key")
                if key in owners and owners[key] == email:
                    return httpx.Response(200, json={
                        "mode": "authenticated",
                        "checkout_url": "https://checkout.example.test/session",
                    })
                return httpx.Response(200, json={"mode": "email_sent"})
            return httpx.Response(200, json={"tiers": []})

        def client(**kwargs):
            return real_client(**kwargs, transport=httpx.MockTransport(respond))

        mock = patch.object(self.server.httpx, "Client", side_effect=client)
        mock.start()
        self.addCleanup(mock.stop)

    def assert_authenticated(self, result, key="test-owner-key"):
        self.assertEqual(result, {
            "mode": "authenticated",
            "checkout_url": "https://checkout.example.test/session",
        })
        request = self.requests[-1]
        self.assertEqual(request.headers["X-API-Key"], key)
        self.assertEqual(request.url.query, b"")
        self.assertNotIn(key, request.content.decode())
        self.assertNotIn(key, json.dumps(result))

    def test_configured_key_reaches_owner_authenticated_flow(self):
        self.server.API_KEY = "test-owner-key"
        result = self.server.parlayapi_checkout_link("owner@example.test", "pro")
        self.assert_authenticated(result)
        self.assertEqual(json.loads(self.requests[0].content), {
            "email": "owner@example.test", "tier": "pro",
        })
        self.assertEqual(self.requests[0].headers["User-Agent"],
                         f"parlayapi-mcp/{self.server._VERSION}")

    def test_environment_alias_still_supplies_optional_key(self):
        self.server = load_server({"PARLAY_API_KEY": " test-owner-key "})
        result = self.server.parlayapi_checkout_link("owner@example.test")
        self.assert_authenticated(result)

    def test_request_key_takes_precedence_and_reset_restores_environment(self):
        self.server.API_KEY = "test-environment-key"
        token = self.server.set_request_api_key(" test-owner-key ")
        try:
            result = self.server.parlayapi_checkout_link("owner@example.test")
            self.assert_authenticated(result)
        finally:
            self.server._REQUEST_API_KEY.reset(token)
        self.assertEqual(self.server.current_api_key(), "test-environment-key")

    def test_keyless_checkout_preserves_opaque_email_acknowledgement(self):
        result = self.server.parlayapi_checkout_link("owner@example.test")
        self.assertEqual(result, {"mode": "email_sent"})
        self.assertNotIn("X-API-Key", self.requests[0].headers)
        self.assertEqual(len(self.requests), 1)

    def test_wrong_key_is_left_for_backend_ownership_validation(self):
        self.server.API_KEY = "test-wrong-owner-key"
        result = self.server.parlayapi_checkout_link("owner@example.test")
        self.assertEqual(result, {"mode": "email_sent"})
        self.assertEqual(self.requests[0].headers["X-API-Key"], "test-wrong-owner-key")
        self.assertEqual(len(self.requests), 1)

    def test_mismatched_email_preserves_backend_acknowledgement(self):
        self.server.API_KEY = "test-owner-key"
        result = self.server.parlayapi_checkout_link("different@example.test")
        self.assertEqual(result, {"mode": "email_sent"})
        self.assertEqual(self.requests[0].headers["X-API-Key"], "test-owner-key")

    def test_keyless_discovery_and_signup_do_not_forward_configured_key(self):
        self.server.API_KEY = "test-owner-key"
        self.server.parlayapi_get_pricing()
        self.server.parlayapi_signup("owner@example.test")
        self.server.parlayapi_magic_link("owner@example.test")
        self.assertEqual(len(self.requests), 3)
        for request in self.requests:
            self.assertNotIn("X-API-Key", request.headers)

    def test_optional_checkout_does_not_relax_required_key_tools(self):
        with self.assertRaisesRegex(RuntimeError, "No ParlayAPI key available"):
            self.server._client()

    def test_concurrent_request_keys_do_not_cross_or_leak_after_reset(self):
        self.server.API_KEY = "test-environment-key"
        barrier = threading.Barrier(2)

        def checkout(key, email):
            token = self.server.set_request_api_key(key)
            try:
                barrier.wait(timeout=3)
                result = self.server.parlayapi_checkout_link(email)
                bound = self.server.current_api_key()
            finally:
                self.server._REQUEST_API_KEY.reset(token)
            return result, bound, self.server.current_api_key()

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(checkout, "test-owner-key", "owner@example.test"),
                pool.submit(checkout, "test-second-key", "second@example.test"),
            ]
            results = [future.result(timeout=5) for future in futures]
        for (result, bound, reset), key in zip(
            results, ("test-owner-key", "test-second-key"),
        ):
            self.assertEqual(result["mode"], "authenticated")
            self.assertEqual(bound, key)
            self.assertEqual(reset, "test-environment-key")
        self.assertEqual(self.server.current_api_key(), "test-environment-key")
        observed = {
            (r.headers.get("X-API-Key"), json.loads(r.content)["email"])
            for r in self.requests
        }
        self.assertEqual(observed, {
            ("test-owner-key", "owner@example.test"),
            ("test-second-key", "second@example.test"),
        })


if __name__ == "__main__":
    unittest.main()
