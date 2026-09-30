def test_health_check(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_corpus_version(client):
    res = client.get("/api/v1/corpus/version")
    assert res.status_code == 200
    data = res.json()
    assert "corpus_version" in data
    assert "latest_amendments_indexed" in data

def test_readiness_is_safe_and_reports_degraded_dependencies(client):
    res = client.get("/api/v1/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in {"ready", "degraded"}
    assert set(data["checks"]) == {"database", "rag_service", "providers"}
    assert data["secrets_included"] is False
    assert "api_key" not in res.text.lower()
    assert "password" not in res.text.lower()
