def test_query_grounded_answer_india(client):
    session_res = client.post("/api/v1/session")
    session_id = session_res.json()["session_id"]

    query_res = client.post(
        "/api/v1/query",
        json={
            "session_id": session_id,
            "query_text": "Can I patent a classical formulation from Charaka Samhita?",
            "jurisdiction": "India",
            "classification_context": "Classical/Generic Medicine"
        }
    )
    assert query_res.status_code == 200
    data = query_res.json()
    assert "query_id" in data
    assert len(data["citations"]) > 0
    assert data["citations"][0]["source_title"] == "Patents Act, 1970"
    assert data["citations"][0]["section_or_article"] == "Section 3(p)"
    assert data["confidence_label"] in ["High", "Medium"]
    assert not data["abstained"]
    assert "disclaimer" in data

def test_query_abstention_out_of_scope(client):
    session_res = client.post("/api/v1/session")
    session_id = session_res.json()["session_id"]

    query_res = client.post(
        "/api/v1/query",
        json={
            "session_id": session_id,
            "query_text": "What is the capital of France and how to make pizza?",
            "jurisdiction": "India"
        }
    )
    assert query_res.status_code == 200
    data = query_res.json()
    assert data["abstained"] is True
    assert data["escalation_suggested"] is True
    assert len(data["citations"]) == 0

def test_query_international_jurisdiction(client):
    session_res = client.post("/api/v1/session")
    session_id = session_res.json()["session_id"]

    query_res = client.post(
        "/api/v1/query",
        json={
            "session_id": session_id,
            "query_text": "What are the genetic resource disclosure rules under WIPO and TRIPS?",
            "jurisdiction": "International"
        }
    )
    assert query_res.status_code == 200
    data = query_res.json()
    assert len(data["citations"]) > 0
    assert data["citations"][0]["jurisdiction"] == "International"
