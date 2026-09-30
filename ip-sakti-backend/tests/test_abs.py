def test_abs_checklist_classical(client):
    res = client.get("/api/v1/abs/checklist?classification=Classical/Generic Medicine")
    assert res.status_code == 200
    data = res.json()
    assert data["classification"] == "Classical/Generic Medicine"
    assert len(data["checklist"]) > 0
    assert any("State Biodiversity Board" in item for item in data["checklist"])

def test_abs_checklist_new_drug(client):
    res = client.get("/api/v1/abs/checklist?classification=New/Non-classical Drug")
    assert res.status_code == 200
    data = res.json()
    assert len(data["checklist"]) > 0
    assert any("National Biodiversity Authority" in item for item in data["checklist"])

def test_abs_checklist_all_categories(client):
    categories = [
        "Classical/Generic Medicine",
        "Patent-or-Proprietary Medicine",
        "New/Non-classical Drug",
        "Phytopharmaceutical",
        "Ayurveda-Aahar/Nutraceutical",
        "Cosmetic",
    ]
    for cat in categories:
        res = client.get(f"/api/v1/abs/checklist?classification={cat}")
        assert res.status_code == 200
        data = res.json()
        assert len(data["checklist"]) > 0
