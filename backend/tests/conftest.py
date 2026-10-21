import socket

import pytest

from app.domain.models import PatientContext, QueryRequest


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    # Windows asyncio builds its wake-up socketpair over the loopback interface.
    # Allow only that local traffic; all external connections remain forbidden.
    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex

    def guarded(original):
        def connect(sock, address):
            if not isinstance(address, tuple) or address[0] not in ("127.0.0.1", "::1"):
                raise AssertionError("M0 tests must not open outbound sockets")
            return original(sock, address)

        return connect

    monkeypatch.setattr(socket.socket, "connect", guarded(original_connect))
    monkeypatch.setattr(socket.socket, "connect_ex", guarded(original_connect_ex))


@pytest.fixture
def request_payload():
    return QueryRequest(
        synthetic_only=True,
        question="耳部测试条目",
        patient=PatientContext(chief_complaint="合成主诉", duration="合成时长"),
    )
