def test_tkdl_lookup_found(client):
    res = client.get("/api/v1/tkdl/lookup?keyword=Ashwagandha")
    assert res.status_code == 200
    data = res.json()
    assert "matches" in data
    assert len(data["matches"]) > 0
    assert "Ashwagandha" in data["matches"][0]["formulation_keyword"]
    assert data["matches"][0]["is_illustrative"] is True
