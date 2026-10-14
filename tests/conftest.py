"""Default-deny X egress. A test must install an explicit mock to use the adapter."""
import pytest
from app import x_api


@pytest.fixture(autouse=True)
def no_paid_services(monkeypatch):
    monkeypatch.setenv('X_BEARER_TOKEN', '')
    monkeypatch.setenv('X_LIVE_ENABLED', 'false')
    monkeypatch.setenv('OPENAI_API_KEY', '')
    def deny():
        raise AssertionError('Real X traffic forbidden in tests; install MockTransport')
    monkeypatch.setattr(x_api, 'client', deny)
