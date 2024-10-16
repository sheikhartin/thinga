import os
import shutil
import mimetypes
from datetime import datetime, timezone
from typing import Optional

from fastapi import UploadFile, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from thinga import models, schemas, enums, utils
from thinga.config import (
    GALLERY_STORAGE_PATH,
    AVATARS_STORAGE_PATH,
    MAX_IMAGE_SIZE_BYTES,
)


def get_user_by_id(*, db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(
    *,
    db: Session,
    username: str,
) -> Optional[models.User]:
    return (
        db.query(models.User).filter(models.User.username == username).first()
    )


def get_user_by_email(*, db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(*, db: Session, user: schemas.UserCreate) -> models.User:
    if get_user_by_username(db=db, username=user.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username `{user.username}` already registered.",
        )
    elif get_user_by_email(db=db, email=user.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email `{user.email}` already registered.",
        )

    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    avatar_file_name = (
        save_image_file(
            file=user.avatar_file,
            storage_path=AVATARS_STORAGE_PATH,
        )
        if user.avatar_file is not None
        else None
    )
    db_profile = models.Profile(
        display_name=user.display_name,
        avatar_file=avatar_file_name,
        bio=user.bio,
        user_id=db_user.id,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return db_user


def get_profile_by_user_id(
    *,
    db: Session,
    user_id: int,
) -> Optional[models.Profile]:
    return (
        db.query(models.Profile)
        .filter(models.Profile.user_id == user_id)
        .first()
    )


def get_images(*, db: Session) -> list[models.Image]:
    return db.query(models.Image).all()


def get_two_random_images(*, db: Session) -> list[models.Image]:
    return db.query(models.Image).order_by(func.random()).limit(2).all()


def get_image_by_id(*, db: Session, image_id: int) -> Optional[models.Image]:
    return db.query(models.Image).filter(models.Image.id == image_id).first()


def create_image(*, db: Session, image: schemas.ImageCreate) -> models.Image:
    file_name = save_image_file(
        file=image.media_file,
        storage_path=GALLERY_STORAGE_PATH,
    )
    db_image = models.Image(media_file=file_name, alt_text=image.alt_text)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def update_image_score(*, db: Session, image_id: int) -> models.Image:
    db_image = get_image_by_id(db=db, image_id=image_id)
    if db_image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found.",
        )
    db_image.score += 1
    db.commit()
    db.refresh(db_image)
    return db_image


def delete_image(*, db: Session, image_id: int) -> None:
    db_image = get_image_by_id(db=db, image_id=image_id)
    if db_image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found.",
        )
    db.delete(db_image)
    db.commit()


def create_rating(
    *,
    db: Session,
    rating: schemas.RatingCreate,
) -> models.Rating:
    db_rating = models.Rating(user_id=rating.user_id, image_id=rating.image_id)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


def get_session_by_access_token(
    *,
    db: Session,
    access_token: str,
) -> Optional[models.Session]:
    return (
        db.query(models.Session)
        .filter(models.Session.access_token == access_token)
        .first()
    )


def create_session(
    *,
    db: Session,
    user_id: int,
    client_fingerprint: str,
) -> models.Session:
    db_session = models.Session(
        client_fingerprint=client_fingerprint,
        user_id=user_id,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def deactivate_session(*, db: Session, access_token: str) -> None:
    db_session = get_session_by_access_token(db=db, access_token=access_token)
    if db_session is not None:
        db_session.status = enums.SessionStatus.INACTIVE
        db.commit()


def verify_session(
    *,
    db: Session,
    access_token: str,
    client_fingerprint: str,
) -> Optional[models.Session]:
    db_session = get_session_by_access_token(db=db, access_token=access_token)
    if (
        db_session is None
        or db_session.status
        in (
            enums.SessionStatus.INACTIVE,
            enums.SessionStatus.EXPIRED,
        )
        or db_session.client_fingerprint != client_fingerprint
    ):
        return None
    elif db_session.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(
        timezone.utc
    ):
        db_session.status = enums.SessionStatus.EXPIRED
        db.commit()

    return db_session


def save_image_file(*, file: UploadFile, storage_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type not in (
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/bmp",
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file must be an image.",
        )
    elif file.size > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                "Image file size exceeds the limit of "
                f"{MAX_IMAGE_SIZE_BYTES / (1024 * 1024)} MB."
            ),
        )

    file_name = utils.generate_unique_file_name(file.filename)
    file_path = os.path.join(storage_path, file_name)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return file_name
