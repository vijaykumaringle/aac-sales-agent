from fastapi.testclient import TestClient

from app.main import app, enquiries


client = TestClient(app)


def setup_function() -> None:
    enquiries.clear()


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_enquiry_marks_it_for_review() -> None:
    response = client.post(
        "/enquiries",
        json={
            "customer_name": "Asha Builders",
            "phone_number": "+919000000000",
            "location": "Pune",
            "requirement_summary": "AAC blocks for a residential project.",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "customer_name": "Asha Builders",
        "phone_number": "+919000000000",
        "location": "Pune",
        "requirement_summary": "AAC blocks for a residential project.",
        "preferred_contact_time": None,
        "status": "pending_review",
    }
