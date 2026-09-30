def test_classification_flow_classical(client):
    # 1. Create session
    session_res = client.post("/api/v1/session")
    session_id = session_res.json()["session_id"]

    # 2. Start classification
    start_res = client.post("/api/v1/classification/start", json={"session_id": session_id})
    assert start_res.status_code == 200
    q_data = start_res.json()
    assert q_data["question_id"] == "q1"
    assert "options" in q_data

    # 3. Answer "Yes" -> Classical formulation result
    answer_res = client.post(
        "/api/v1/classification/answer",
        json={
            "session_id": session_id,
            "question_id": "q1",
            "answer": "Yes"
        }
    )
    assert answer_res.status_code == 200
    res_data = answer_res.json()
    assert res_data["classification_result"] == "Classical/Generic Medicine"
    assert "Section 3(p)" in res_data["explanation"]
    assert "Patents" in res_data["relevant_regimes"]

def test_classification_flow_phytopharmaceutical(client):
    session_res = client.post("/api/v1/session")
    session_id = session_res.json()["session_id"]

    # Start
    client.post("/api/v1/classification/start", json={"session_id": session_id})

    # Answer No to q1 -> receives q2
    q2_res = client.post(
        "/api/v1/classification/answer",
        json={"session_id": session_id, "question_id": "q1", "answer": "No"}
    )
    assert q2_res.json()["next_question_id"] == "q2_non_classical"

    # Answer Therapeutic to q2 -> receives q3
    q3_res = client.post(
        "/api/v1/classification/answer",
        json={"session_id": session_id, "question_id": "q2_non_classical", "answer": "Therapeutic Treatment"}
    )
    assert q3_res.json()["next_question_id"] == "q3_therapeutic"

    # Answer Botanical fraction -> receives Phytopharmaceutical final result
    final_res = client.post(
        "/api/v1/classification/answer",
        json={"session_id": session_id, "question_id": "q3_therapeutic", "answer": "Standardized Botanical Fraction"}
    )
    assert final_res.status_code == 200
    data = final_res.json()
    assert data["classification_result"] == "Phytopharmaceutical"
    assert "CDSCO" in str(data["required_regulatory_checks"])
