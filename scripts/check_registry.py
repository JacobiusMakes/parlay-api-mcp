"""Check published-package ownership and registry metadata before distribution."""

import argparse
import json
import os
from pathlib import Path
import tomllib
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
NAME = "io.github.JacobiusMakes/parlayapi"


def get_json(url):
    request = Request(url, headers={"User-Agent": "parlayapi-registry-check/1.0"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def normalize_optional_fields(value):
    """The registry omits isRequired=false when serializing optional inputs."""
    if isinstance(value, dict):
        return {
            key: normalize_optional_fields(item)
            for key, item in value.items()
            if not (key == "isRequired" and item is False)
        }
    if isinstance(value, list):
        return [normalize_optional_fields(item) for item in value]
    return value


def check(check_published=False, allow_unpublished_package=False):
    if allow_unpublished_package and (
        os.environ.get("GITHUB_EVENT_NAME") != "pull_request" or check_published
    ):
        raise ValueError("Unpublished packages are allowed only during pull-request preflight")
    manifest = json.loads((ROOT / "server.official.json").read_text())
    schema = get_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(manifest)
    assert manifest == json.loads((ROOT / "registry/server.json").read_text()), "Registry copies differ"
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    assert manifest["name"] == NAME
    assert manifest["version"] == version
    assert manifest["repository"]["url"] == "https://github.com/JacobiusMakes/parlay-api-mcp"
    assert json.loads((ROOT / "server.json").read_text())["version"] == version
    assert manifest["remotes"][0]["url"] == "https://parlay-api.com/mcp/http"
    assert manifest["remotes"][0]["type"] == "streamable-http"
    package = manifest["packages"][0]
    assert (package["registryType"], package["identifier"], package["version"]) == ("pypi", "parlayapi-mcp", version)
    ownership_marker = f"mcp-name: {NAME}"
    assert ownership_marker in (ROOT / "README.md").read_text(), "README ownership marker missing"
    package_unpublished = False
    try:
        published = get_json(f"https://pypi.org/pypi/parlayapi-mcp/{version}/json")
    except HTTPError as error:
        if error.code != 404 or not allow_unpublished_package:
            raise
        package_unpublished = True
    else:
        assert published["info"]["version"] == version
        assert ownership_marker in published["info"]["description"], "PyPI ownership marker missing"
        assert published["urls"] and all(not file["yanked"] for file in published["urls"])
    tag = os.environ.get("GITHUB_REF", "")
    if tag.startswith("refs/tags/"):
        assert tag == f"refs/tags/v{version}", "Release tag and package version differ"
    needs_publish = True
    url = f"https://registry.modelcontextprotocol.io/v0/servers/{quote(NAME, safe='')}/versions/{quote(version, safe='')}"
    try:
        existing = get_json(url)["server"]
    except HTTPError as error:
        if error.code != 404:
            raise
    else:
        assert normalize_optional_fields(existing) == normalize_optional_fields(manifest), "This registry version already exists with different metadata; choose a new version"
        needs_publish = False
    if check_published:
        assert not needs_publish, "Registry version is not published"
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a") as handle:
            handle.write(f"needs_publish={str(needs_publish).lower()}\n")
    print(f"Validated {NAME}@{version}: schema, manifest parity, README ownership, remote transport.")
    if package_unpublished:
        print("PyPI version is unpublished; allowed for pull-request preflight only.")
    else:
        print("Published PyPI package and ownership verified.")
    print("Registry publication needed." if needs_publish else "Exact metadata already published.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published", action="store_true")
    parser.add_argument(
        "--allow-unpublished-package", action="store_true",
        help="Allow a PyPI 404 during pull-request preflight only",
    )
    args = parser.parse_args()
    check(args.published, args.allow_unpublished_package)
