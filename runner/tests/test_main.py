from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "runner"}


def test_run_is_not_implemented_yet():
    response = client.post("/run", json={"source": "int main(void) { return 0; }"})

    assert response.status_code == 501
