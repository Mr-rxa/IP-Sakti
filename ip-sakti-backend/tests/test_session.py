def test_create_session(client):
    response = client.post("/api/v1/session")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "created_at" in data
    assert data["jurisdiction_selected"] == "India"

def test_set_jurisdiction(client):
    create_res = client.post("/api/v1/session")
    session_id = create_res.json()["session_id"]

    patch_res = client.patch(
        f"/api/v1/session/{session_id}/jurisdiction",
        json={"jurisdiction": "International"}
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["session_id"] == session_id
    assert data["jurisdiction"] == "International"

def test_invalid_session_jurisdiction(client):
    patch_res = client.patch(
        "/api/v1/session/invalid-session-id/jurisdiction",
        json={"jurisdiction": "International"}
    )
    assert patch_res.status_code == 404
    data = patch_res.json()
    assert data["error_code"] == "SESSION_NOT_FOUND"
