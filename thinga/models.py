import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Enum,
    DateTime,
)
from sqlalchemy.orm import relationship

from thinga import enums
from thinga.database import Base
from thinga.config import SESSION_EXPIRE_DAYS


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(35), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(65))
    role = Column(Enum(enums.UserRole), default=enums.UserRole.USER)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="user", uselist=False)
    ratings = relationship("Rating", back_populates="user")
    sessions = relationship("Session", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String(50), nullable=False)
    avatar_file = Column(String(35), default="default.jpg")
    bio = Column(String(300))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="profile")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    media_file = Column(String(35), nullable=False)
    alt_text = Column(String(250))
    score = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ratings = relationship("Rating", back_populates="image")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="ratings")
    image = relationship("Image", back_populates="ratings")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(
        String(32),
        default=lambda: uuid.uuid4().hex,
        unique=True,
        index=True,
    )
    client_fingerprint = Column(String(64), nullable=False)
    status = Column(
        Enum(enums.SessionStatus),
        default=enums.SessionStatus.ACTIVE,
    )
    expires_at = Column(
        DateTime,
        default=lambda: (
            datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRE_DAYS)
        ),
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="sessions")
