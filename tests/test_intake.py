from fastapi.testclient import TestClient

from app.main import app


def send(client: TestClient, text: str) -> dict:
    response = client.post(
        "/intake/messages",
        json={"channel": "whatsapp", "contact_identifier": "+919000000000", "message_text": text},
    )
    assert response.status_code == 200
    return response.json()


def test_intake_converts_a_completed_conversation_to_pending_review_enquiry() -> None:
    with TestClient(app) as client:
        first_reply = send(client, "Hello")
        assert first_reply["next_step"] == "customer_name"

        assert send(client, "Asha Builders")["next_step"] == "location"
        assert send(client, "Pune")["next_step"] == "project_type"
        assert send(client, "Residential")["next_step"] == "estimated_quantity"
        assert send(client, "10,000 blocks")["next_step"] == "requirement_summary"
        assert send(client, "200 mm blocks, delivery next week")["next_step"] == "preferred_contact_time"
        final_reply = send(client, "Tuesday morning")
        enquiry = client.get(f"/enquiries/{final_reply['enquiry_id']}").json()

    assert final_reply["next_step"] == "completed"
    assert "quotation is not generated" in final_reply["reply_text"]
    assert enquiry["status"] == "pending_review"
    assert enquiry["source"] == "whatsapp"
    assert enquiry["customer_name"] == "Asha Builders"
