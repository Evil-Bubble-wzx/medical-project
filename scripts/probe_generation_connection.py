"""Credential-free connectivity probe; never prints proxy values or exception bodies."""

import os

import httpx

print(
    "proxy_variables_present",
    [key for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY") if os.environ.get(key)],
)
for mode in (False, True):
    try:
        response = httpx.get("https://api.deepseek.com", trust_env=mode, timeout=15)
        print("trust_env", mode, "status", response.status_code)
    except Exception as error:
        chain = []
        while error is not None and len(chain) < 6:
            chain.append(type(error).__name__)
            error = error.__cause__
        print("trust_env", mode, "error_types", chain)
