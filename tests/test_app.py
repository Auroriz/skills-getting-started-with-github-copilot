import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def activities(monkeypatch):
    test_activities = {
        "Chess Club": app_module.Activity(
            "Chess Club",
            "Learn strategies and compete in chess tournaments",
            "Fridays, 3:30 PM - 5:00 PM",
            2,
            ["existing@example.com"],
        ),
        "Full Activity": app_module.Activity(
            "Full Activity",
            "An activity at capacity",
            "Mondays, 3:30 PM - 5:00 PM",
            1,
            ["existing@example.com"],
        ),
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


@pytest.fixture
def client(activities):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_details(client, activities):
    # Arrange
    expected_chess_club = {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 2,
        "participants": ["existing@example.com"],
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "Chess Club": expected_chess_club,
        "Full Activity": {
            "description": "An activity at capacity",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 1,
            "participants": ["existing@example.com"],
        },
    }


def test_signup_adds_normalized_email(client, activities):
    # Arrange
    email = "  New.Student@Example.com  "

    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new.student@example.com for Chess Club"}
    assert "new.student@example.com" in activities["Chess Club"].participants


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": "student@example.com"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_for_blank_email(client):
    # Arrange
    email = "  "

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Email is required"}


def test_signup_returns_400_for_duplicate_email(client):
    # Arrange
    email = "EXISTING@example.com"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "existing@example.com is already signed up for Chess Club"
    }


def test_signup_returns_400_when_activity_is_full(client):
    # Arrange
    email = "new.student@example.com"

    # Act
    response = client.post("/activities/Full Activity/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Full Activity is full"}


def test_remove_participant_removes_normalized_email(client, activities):
    # Arrange
    email = "  EXISTING@Example.com  "

    # Act
    response = client.delete(
        "/activities/Chess Club/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Removed existing@example.com from Chess Club"}
    assert "existing@example.com" not in activities["Chess Club"].participants


def test_remove_participant_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_returns_400_for_blank_email(client):
    # Arrange
    email = "  "

    # Act
    response = client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Email is required"}


def test_remove_participant_returns_400_when_email_is_not_signed_up(client):
    # Arrange
    email = "missing@example.com"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "missing@example.com is not signed up for Chess Club"
    }