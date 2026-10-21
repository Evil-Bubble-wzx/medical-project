import importlib.util
from pathlib import Path

import httpx
import pytest


def load_check():
    path = Path(__file__).resolve().parents[2] / "scripts/check_deepseek_key.py"
    spec = importlib.util.spec_from_file_location("credential_check", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("status,expected", [(200, 0), (401, 2), (402, 3), (500, 3)])
def test_authentication_check_is_read_only_and_redacted(monkeypatch, capsys, status, expected):
    module = load_check()
    monkeypatch.setenv("DEEPSEEK_API_KEY", "SYNTHETIC_KEY")
    real_client = httpx.Client
    seen = []

    def handler(request):
        seen.append(1)
        assert request.method == "GET" and request.url.path == "/models"
        assert request.headers["Authorization"] == "Bearer SYNTHETIC_KEY"
        assert not request.content
        return httpx.Response(status, text="PRIVATE_RESPONSE SYNTHETIC_KEY")

    monkeypatch.setattr(
        module.httpx, "Client", lambda **kwargs: real_client(transport=httpx.MockTransport(handler))
    )
    assert module.main() == expected and len(seen) == 1
    output = capsys.readouterr().out
    assert "SYNTHETIC_KEY" not in output and "PRIVATE_RESPONSE" not in output


@pytest.mark.parametrize("key", ["", "with whitespace", "非ASCII密钥"])
def test_invalid_key_shape_does_not_connect(monkeypatch, capsys, key):
    module = load_check()
    monkeypatch.setenv("DEEPSEEK_API_KEY", key)
    monkeypatch.setattr(module.httpx, "Client", lambda **kwargs: pytest.fail("must not connect"))
    assert module.main() == 2
    assert "非ASCII" not in capsys.readouterr().out


def test_connection_failure_does_not_print_exception(monkeypatch, capsys):
    module = load_check()
    monkeypatch.setenv("DEEPSEEK_API_KEY", "SYNTHETIC_KEY")
    real_client = httpx.Client

    def handler(request):
        raise httpx.ConnectError("PRIVATE_PROXY SYNTHETIC_KEY")

    monkeypatch.setattr(
        module.httpx, "Client", lambda **kwargs: real_client(transport=httpx.MockTransport(handler))
    )
    assert module.main() == 3
    assert "PRIVATE_PROXY" not in capsys.readouterr().out
