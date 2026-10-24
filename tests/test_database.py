from fastapi.testclient import TestClient

from app.main import app
from app.db import database


def test_app_startup_does_not_connect_to_or_initialize_database(monkeypatch) -> None:
    def fail_if_connected():
        raise AssertionError("Application startup must not connect to the database")

    monkeypatch.setattr(database, "connection", fail_if_connected)

    with TestClient(app) as client:
        health_response = client.get("/health")
        docs_response = client.get("/docs")

    assert health_response.status_code == 200
    assert docs_response.status_code == 200
