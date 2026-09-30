def test_escalate(client):
    res = client.post(
        "/api/v1/escalate",
        json={
            "session_id": "test-session-id",
            "query_id": "test-query-id",
            "user_contact_optional": "vaidya@example.com",
            "reason": "Need specialized patent attorney consultation for classical extraction variant"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "queued"
    assert data["expert_assigned"] is False
    assert "No human expert" in data["message"]
    assert "escalation_id" in data
