from datetime import datetime
from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field, EmailStr

from thinga import enums


class ProfileBase(BaseModel):
    display_name: str = Field(..., min_length=3, max_length=50)
    avatar_file: Optional[str] = Field(None, max_length=35)
    bio: Optional[str] = Field(None, max_length=300)


class ProfileCreate(ProfileBase):
    avatar_file: Optional[UploadFile] = None


class Profile(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., ge=1)
    user_id: int = Field(..., ge=1)


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=35)
    email: EmailStr


class UserCreate(UserBase, ProfileCreate):
    password: str = Field(..., min_length=8, max_length=65)


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., ge=1)
    role: enums.UserRole
    created_at: datetime
    profile: Optional[Profile] = None


class UserProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=35)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=65)
    display_name: Optional[str] = Field(None, min_length=3, max_length=50)
    bio: Optional[str] = Field(None, max_length=300)
    avatar_file: Optional[UploadFile] = None


class ImageBase(BaseModel):
    media_file: str = Field(..., max_length=35)
    alt_text: Optional[str] = Field(None, max_length=250)


class ImageCreate(ImageBase):
    media_file: UploadFile


class Image(ImageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., ge=1)
    score: int = Field(..., ge=0)
    created_at: datetime


class RatingBase(BaseModel):
    user_id: int = Field(..., ge=1)
    image_id: int = Field(..., ge=1)


class RatingCreate(RatingBase):
    pass


class Rating(RatingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., ge=1)
    created_at: datetime
