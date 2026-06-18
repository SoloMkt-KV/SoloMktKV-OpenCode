#!/usr/bin/env python3
"""SoloMkt-KV helper for OpenCode/Codex plugin workflows."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://solosmart-uat.issmart.com.cn/solomkt_kv/api/v1"
DEFAULT_HOME = Path.home() / ".solomkt-kv"
DEFAULT_TIMEOUT_SECONDS = 600


class KVError(Exception):
    """Expected user-facing workflow error."""


def _configured_home() -> str | None:
    return os.environ.get("SoloMkt-KV_HOME") or os.environ.get("SOLOMKT_KV_HOME")


def credential_path() -> Path:
    configured = _configured_home()
    root = Path(configured).expanduser() if configured else DEFAULT_HOME
    return root / ".credentials.json"


def read_credentials() -> dict[str, Any]:
    path = credential_path()
    if not path.exists():
        raise KVError(
            "SoloMkt-KV API key is not configured. Configure it first at "
            f"{path}."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KVError(f"Credentials file is not valid JSON: {path}") from exc

    api_key = data.get("apiKey") or data.get("api_key") or data.get("x-api-key")
    if not isinstance(api_key, str) or not api_key.strip():
        raise KVError(f"Credentials file does not contain apiKey: {path}")

    base_url = data.get("baseUrl") or data.get("base_url") or DEFAULT_BASE_URL
    if not isinstance(base_url, str) or not base_url.strip():
        raise KVError(f"Credentials file contains an invalid baseUrl: {path}")

    return {
        "apiKey": api_key.strip(),
        "baseUrl": base_url.rstrip("/"),
    }


def write_credentials(api_key: str, base_url: str) -> Path:
    api_key = api_key.strip()
    if not api_key:
        raise KVError("API key cannot be empty.")

    path = credential_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 1,
        "baseUrl": base_url.rstrip("/"),
        "apiKey": api_key,
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path


def http_json(
    method: str,
    url: str,
    api_key: str,
    body: dict[str, Any] | None,
    timeout: int,
) -> Any:
    encoded = None
    headers = {"x-api-key": api_key, "Accept": "application/json"}
    if body is not None:
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url=url,
        data=encoded,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise KVError(f"HTTP {exc.code} from SoloMkt-KV API: {detail}") from exc
    except urllib.error.URLError as exc:
        raise KVError(f"Unable to reach SoloMkt-KV API: {exc}") from exc
    except TimeoutError as exc:
        raise KVError(f"SoloMkt-KV API request timed out after {timeout} seconds.") from exc

    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise KVError(f"API returned non-JSON response: {raw[:500]}") from exc


def fetch_models(timeout: int) -> dict[str, Any]:
    credentials = read_credentials()
    url = f"{credentials['baseUrl']}/models?type=all"
    payload = http_json("GET", url, credentials["apiKey"], None, timeout)
    if not isinstance(payload, dict) or payload.get("success") is not True:
        rendered = json.dumps(payload, ensure_ascii=False)
        raise KVError(f"Model API did not return success=true: {rendered}")
    return payload


def flatten_models(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data") if isinstance(payload, dict) else {}
    models: list[dict[str, Any]] = []
    for group in ("system", "custom"):
        values = (data or {}).get(group, []) or []
        for item in values:
            if isinstance(item, dict):
                model = dict(item)
                model["group"] = group
                models.append(model)
    return models


def print_models(payload: dict[str, Any], as_json: bool) -> None:
    models = flatten_models(payload)
    if as_json:
        print(json.dumps(models, ensure_ascii=False, indent=2))
        return

    if not models:
        print("No public SoloMkt-KV models are currently available.")
        return

    print("Available SoloMkt-KV models:")
    for index, model in enumerate(models, start=1):
        tags = ", ".join(str(tag) for tag in model.get("tags") or [])
        sub = model.get("sub") or ""
        preview = model.get("previewImageUrl") or ""
        tag_text = f" | tags: {tags}" if tags else ""
        sub_text = f" | sub: {sub}" if sub else ""
        preview_text = f" | preview: {preview}" if preview else ""
        print(
            f"{index}. id={model.get('id')} | name: {model.get('name')}"
            f"{sub_text}{tag_text}{preview_text}"
        )


def validate_required(name: str, value: str, maximum: int) -> str:
    value = value.strip()
    if not value:
        raise KVError(f"{name} is required.")
    if len(value) > maximum:
        raise KVError(f"{name} must be at most {maximum} characters.")
    return value


def validate_poster_size(value: str) -> str:
    value = value.strip()
    if not value:
        return '["16:9"]'
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise KVError('posterSize must be a JSON string such as ["16:9"].') from exc
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise KVError('posterSize must be a JSON array string such as ["16:9"].')
    return json.dumps(parsed, ensure_ascii=False)


def generate(args: argparse.Namespace) -> list[str]:
    credentials = read_credentials()
    model_id = validate_required("modelId", args.model_id, 200)
    activity_name = validate_required("activityName", args.activity_name, 200)
    activity_theme = validate_required("activityTheme", args.activity_theme, 200)
    activity_time = validate_required("activityTime", args.activity_time, 200)
    activity_location = validate_required("activityLocation", args.activity_location, 200)
    prompt = args.prompt.strip()
    if prompt and len(prompt) > 1000:
        raise KVError("prompt must be at most 1000 characters.")

    print("Fetching the latest SoloMkt-KV model list before generation...", file=sys.stderr)
    models_payload = fetch_models(min(args.timeout, 60))
    model_ids = {str(model.get("id")) for model in flatten_models(models_payload)}
    if model_id not in model_ids:
        raise KVError(
            "Selected modelId was not found in the latest model list. "
            "Fetch models again and ask the user to choose one of the returned IDs."
        )

    body = {
        "modelId": model_id,
        "activityName": activity_name,
        "activityTheme": activity_theme,
        "activityTime": activity_time,
        "activityLocation": activity_location,
        "posterQuality": args.poster_quality.strip() or "2K",
        "posterSize": validate_poster_size(args.poster_size),
    }
    if prompt:
        body["prompt"] = prompt

    print(
        "SoloMkt-KV is generating the KV images. This can take several minutes; "
        "the request timeout is 10 minutes.",
        file=sys.stderr,
    )
    url = f"{credentials['baseUrl']}/generateKV"
    result = http_json("POST", url, credentials["apiKey"], body, args.timeout)
    if not isinstance(result, list) or not all(isinstance(item, str) for item in result):
        rendered = json.dumps(result, ensure_ascii=False)
        raise KVError(f"Unexpected generateKV response: {rendered}")
    return result


def command_configure(args: argparse.Namespace) -> None:
    api_key = args.api_key
    if not api_key:
        api_key = getpass.getpass("SoloMkt-KV API key: ")
    path = write_credentials(api_key, args.base_url)
    print(f"Saved SoloMkt-KV credentials to {path}")
    if args.validate:
        payload = fetch_models(args.timeout)
        print(f"Validation passed. {len(flatten_models(payload))} model(s) available.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SoloMkt-KV OpenCode plugin helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("credentials-path", help="Print the resolved credentials path")

    configure = subparsers.add_parser("configure", help="Save a SoloMkt-KV API key")
    configure.add_argument("--api-key", default="", help="API key. Omit to enter it securely.")
    configure.add_argument("--base-url", default=DEFAULT_BASE_URL)
    configure.add_argument(
        "--validate",
        action="store_true",
        help="Validate by calling the models API after saving.",
    )
    configure.add_argument("--timeout", type=int, default=30)

    check = subparsers.add_parser("check-credentials", help="Check configured credentials")
    check.add_argument(
        "--validate",
        action="store_true",
        help="Validate by calling the models API.",
    )
    check.add_argument("--timeout", type=int, default=30)

    models = subparsers.add_parser("models", help="Fetch and print available models")
    models.add_argument("--json", action="store_true")
    models.add_argument("--timeout", type=int, default=30)

    generate_cmd = subparsers.add_parser("generate", help="Generate KV images")
    generate_cmd.add_argument("--model-id", required=True)
    generate_cmd.add_argument("--activity-name", required=True)
    generate_cmd.add_argument("--activity-theme", required=True)
    generate_cmd.add_argument("--activity-time", required=True)
    generate_cmd.add_argument("--activity-location", required=True)
    generate_cmd.add_argument("--prompt", default="")
    generate_cmd.add_argument("--poster-quality", default="2K")
    generate_cmd.add_argument("--poster-size", default='["16:9"]')
    generate_cmd.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "credentials-path":
            print(credential_path())
        elif args.command == "configure":
            command_configure(args)
        elif args.command == "check-credentials":
            path = credential_path()
            read_credentials()
            print(f"Credentials found at {path}")
            if args.validate:
                payload = fetch_models(args.timeout)
                print(f"Validation passed. {len(flatten_models(payload))} model(s) available.")
        elif args.command == "models":
            print_models(fetch_models(args.timeout), args.json)
        elif args.command == "generate":
            urls = generate(args)
            print(json.dumps(urls, ensure_ascii=False, indent=2))
        else:
            parser.error("unknown command")
    except KVError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
