"""Validate provider authentication without patient data or printing credentials/body."""

import json
import os
from pathlib import Path

import httpx


def main():
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "configs/generation.json").read_text(encoding="utf-8"))
    if config["base_url"].rstrip("/") not in (
        "https://api.deepseek.com",
        "https://api.deepseek.com/v1",
    ):
        print("This credential check supports the official DeepSeek HTTPS endpoint only.")
        return 2
    key = os.environ.get(config.get("api_key_env", "DEEPSEEK_API_KEY"), "")
    if not key or any(not 33 <= ord(c) <= 126 for c in key):
        print("API key is empty or contains unexpected whitespace. Enter only the key.")
        return 2
    try:
        with httpx.Client(
            timeout=20,
            trust_env=False,
            follow_redirects=False,
            transport=httpx.HTTPTransport(retries=2, trust_env=False),
        ) as client:
            response = client.get(
                config["base_url"].rstrip("/") + "/models",
                headers={"Authorization": "Bearer " + key},
            )
    except httpx.HTTPError:
        print("Provider connection failed during authentication check. No key was saved.")
        return 3
    if response.status_code == 401:
        print(
            "Provider rejected this key (HTTP 401). "
            "No key was saved; create/check your official API key."
        )
        return 2
    if response.status_code != 200:
        print(
            "Authentication check did not succeed (HTTP "
            + str(response.status_code)
            + "). No key was saved."
        )
        return 3
    print("Provider authentication succeeded. No patient information was sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
