from fastapi.testclient import TestClient

from app.main import app


def test_health_check(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "sales-agent.db"))
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_review_enquiry(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "sales-agent.db"))
    client = TestClient(app)
    create_response = client.post(
        "/enquiries",
        json={
            "customer_name": "Asha Builders",
            "phone_number": "+919000000000",
            "location": "Pune",
            "requirement_summary": "AAC blocks for a residential project.",
            "estimated_quantity": "10,000 blocks",
            "project_type": "Residential",
            "source": "whatsapp",
        },
    )
    assert create_response.status_code == 201
    enquiry = create_response.json()
    assert enquiry["status"] == "pending_review"
    assert enquiry["review_notes"] is None

    review_response = client.patch(
        f"/enquiries/{enquiry['id']}/review",
        json={"status": "contacted", "review_notes": "Call back on Tuesday morning."},
    )
    assert review_response.status_code == 200
    assert review_response.json()["status"] == "contacted"
    assert review_response.json()["review_notes"] == "Call back on Tuesday morning."


def test_list_enquiries_can_filter_by_status(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "sales-agent.db"))
    client = TestClient(app)
    enquiry = client.post(
        "/enquiries",
        json={
            "customer_name": "Asha Builders",
            "phone_number": "+919000000000",
            "location": "Pune",
            "requirement_summary": "AAC blocks for a residential project.",
        },
    ).json()
    client.patch(f"/enquiries/{enquiry['id']}/review", json={"status": "in_review"})
    response = client.get("/enquiries?status=in_review")
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [enquiry["id"]]
