def test_translate_hindi(client):
    res = client.post(
        "/api/v1/translate",
        json={
            "text": "Can I patent this formulation?",
            "target_language": "hi",
            "source_language": "en"
        }
    )
    assert res.status_code == 501
    assert "not configured" in res.json()["detail"]
