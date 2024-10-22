import os
import io
from urllib.parse import urlparse
from unittest.mock import Mock, patch
from typing import Iterator

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from thinga import models, schemas, crud, enums
from thinga.main import app
from thinga.database import Base
from thinga.dependencies import get_db
from thinga.config import TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False
)


@pytest.fixture(scope="function")
def test_db_session() -> Iterator[Session]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(
    test_db_session: Session,
) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        try:
            yield test_db_session
        finally:
            test_db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def create_test_admin_user(test_db_session: Session) -> models.User:
    user_data = schemas.UserCreate(
        username="adminuser",
        email="adminuser@example.com",
        password="testpass123",
        display_name="Admin User",
    )
    crud.create_user(db=test_db_session, user=user_data)
    return crud.update_user_role(
        db=test_db_session,
        username="adminuser",
        new_role=enums.UserRole.ADMIN,
    )


@pytest.fixture(scope="function")
def create_test_user(test_db_session: Session) -> models.User:
    user_data = schemas.UserCreate(
        username="johndoe",
        email="johndoe@example.com",
        password="password123",
        display_name="John Doe",
    )
    return crud.create_user(db=test_db_session, user=user_data)


@pytest.fixture(scope="function")
def create_sample_images(
    test_db_session: Session,
    mock_save_image_file: Mock,
) -> list[models.Image]:
    # Create a BinaryIO object to mimic file upload operations
    image_stream = io.BytesIO(b"image_data")

    cat_image = UploadFile(file=image_stream, filename="cute-cat.jpg")
    cat_image_data = schemas.ImageCreate(
        media_file=cat_image, alt_text="A cute cat image"
    )
    beach_image = UploadFile(
        file=image_stream, filename="a-beach-in-california.jpg"
    )
    beach_image_data = schemas.ImageCreate(
        media_file=beach_image, alt_text="A beach in California"
    )
    rat_image = UploadFile(file=image_stream, filename="rat-in-tunnel.png")
    rat_image_data = schemas.ImageCreate(
        media_file=rat_image, alt_text="A rat in the tunnel"
    )

    sample_images = [
        crud.create_image(db=test_db_session, image=cat_image_data),
        crud.create_image(db=test_db_session, image=beach_image_data),
        crud.create_image(db=test_db_session, image=rat_image_data),
    ]
    return sample_images


@pytest.fixture(scope="session")
def mock_save_image_file() -> Iterator[Mock]:
    with patch("thinga.crud.save_image_file") as mock_save_image_file:
        mock_save_image_file.return_value = "mocked_image_file_path.png"
        yield mock_save_image_file


@pytest.fixture(scope="session", autouse=True)
def teardown_test_database() -> Iterator[None]:
    yield

    parsed_url = urlparse(TEST_DATABASE_URL)
    if parsed_url.scheme in ("sqlite",):
        db_file_path = parsed_url.path.strip("/")
        if os.path.exists(db_file_path):
            os.remove(db_file_path)
            print(f"Removed test database file: {db_file_path}")
        else:
            print(f"Test database file does not exist: {db_file_path}")
