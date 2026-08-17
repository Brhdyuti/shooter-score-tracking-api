from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_shooter():
    response = client.post("/shooters", json={
        "name": "Test Shooter",
        "email": "test_shooter_unique@example.com",
        "join_date": "2026-01-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Shooter"
    assert "id" in data


def test_get_shooters_list():
    response = client.get("/shooters")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_nonexistent_shooter():
    response = client.get("/shooters/99999")
    assert response.status_code == 404


def test_stats_for_shooter_with_scores():
    # shooter_id 1 should already have scores from manual testing
    response = client.get("/shooters/1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "average_percentage" in data
    assert 0 <= data["average_percentage"] <= 100


def test_stats_for_shooter_with_no_data():
    # create a fresh shooter with no sessions/scores
    create_response = client.post("/shooters", json={
        "name": "Empty Shooter",
        "email": "empty_shooter_unique@example.com",
        "join_date": "2026-01-01"
    })
    new_id = create_response.json()["id"]

    response = client.get(f"/shooters/{new_id}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No scores recorded yet"