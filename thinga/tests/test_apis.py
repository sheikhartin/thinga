import os
from unittest.mock import Mock

from fastapi import status
from fastapi.testclient import TestClient

from thinga import models


def test_create_user(test_client: TestClient) -> None:
    response = test_client.post(
        "/users/",
        data={
            "username": "johndoe",
            "email": "johndoe@example.com",
            "password": "password123",
            "display_name": "John Doe",
            "bio": "This is a test bio for John Doe.",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "johndoe"
    assert "id" in data


def test_login_user(
    test_client: TestClient,
    create_test_user: models.User,
) -> None:
    response = test_client.post(
        "/login/", json={"username": "johndoe", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.cookies


def test_read_users_me(
    test_client: TestClient,
    create_test_user: models.User,
) -> None:
    login_response = test_client.post(
        "/login/", json={"username": "johndoe", "password": "password123"}
    )
    access_token = login_response.cookies.get("access_token")
    assert access_token is not None
    test_client.cookies.set("access_token", access_token)

    response = test_client.get("/users/me/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "johndoe"
    assert data["profile"]["display_name"] == "John Doe"
    assert data["profile"]["avatar_file"] == "default.jpg"
    assert data["profile"]["bio"] is None


def test_update_user_profile(
    test_client: TestClient,
    create_test_user: models.User,
    mock_save_image_file: Mock,
) -> None:
    login_response = test_client.post(
        "/login/", json={"username": "johndoe", "password": "password123"}
    )
    access_token = login_response.cookies.get("access_token")
    assert access_token is not None
    test_client.cookies.set("access_token", access_token)

    sample_image_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "sample-image.png"
    )
    with open(sample_image_file, "rb") as f:
        response = test_client.patch(
            "/users/me/",
            data={
                "username": "updateduser",
                "display_name": "Updated User",
            },
            files={
                "avatar_file": (
                    "sample-image.png",
                    f,
                    "image/png",
                )
            },
        )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "updateduser"
    assert data["profile"]["display_name"] == "Updated User"
    assert data["profile"]["avatar_file"] == "mocked_image_file_path.png"


def test_get_images(
    test_client: TestClient,
    create_test_admin_user: models.User,
) -> None:
    response = test_client.get("/images/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)


def test_get_random_images(
    test_client: TestClient,
    create_sample_images: list[models.Image],
) -> None:
    response = test_client.get("/images/random/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_create_image(
    test_client: TestClient,
    create_test_admin_user: models.User,
    mock_save_image_file: Mock,
) -> None:
    login_response = test_client.post(
        "/login/", json={"username": "adminuser", "password": "testpass123"}
    )
    access_token = login_response.cookies.get("access_token")
    assert access_token is not None
    test_client.cookies.set("access_token", access_token)

    sample_image_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "sample-image.png"
    )
    with open(sample_image_file, "rb") as f:
        response = test_client.post(
            "/images/",
            data={
                "alt_text": "Forest or city!?",
            },
            files={
                "media_file": (
                    "sample-image.png",
                    f,
                    "image/png",
                )
            },
        )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["media_file"] is not None


def test_delete_image(
    test_client: TestClient,
    create_test_admin_user: models.User,
    create_sample_images: list[models.Image],
) -> None:
    login_response = test_client.post(
        "/login/", json={"username": "adminuser", "password": "testpass123"}
    )
    access_token = login_response.cookies.get("access_token")
    assert access_token is not None
    test_client.cookies.set("access_token", access_token)

    response = test_client.delete(
        "/images/1/"  # ID 1 represents the photo of the cute cat
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == {"message": "Image deleted successfully."}


def test_rate_image(
    test_client: TestClient,
    create_test_user: models.User,
    create_sample_images: list[models.Image],
) -> None:
    login_response = test_client.post(
        "/login/", json={"username": "johndoe", "password": "password123"}
    )
    access_token = login_response.cookies.get("access_token")
    assert access_token is not None
    test_client.cookies.set("access_token", access_token)

    response = test_client.post("/images/1/rate/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["score"] == 1
