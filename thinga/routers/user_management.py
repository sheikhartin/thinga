from typing import Optional

from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    Body,
    UploadFile,
    File,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from thinga import models, schemas, crud, enums, utils
from thinga.dependencies import (
    get_db,
    get_access_token,
    get_current_user,
    get_admin_or_moderator,
)
from thinga.config import (
    COOKIE_SECURE_MODE,
    COOKIE_NO_JS_ACCESS,
    COOKIE_SAMESITE_POLICY,
)

router = APIRouter()


@router.post("/login/", response_model=schemas.User)
async def login(
    request: Request,
    response: Response,
    username: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db),
):
    db_user = crud.get_user_by_username(db=db, username=username)
    if db_user is None or not utils.verify_password(
        password, db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )

    client_fingerprint = utils.generate_client_fingerprint(request)
    db_session = crud.create_session(
        db=db,
        user_id=db_user.id,
        client_fingerprint=client_fingerprint,
    )
    response.set_cookie(
        key="access_token",
        value=db_session.access_token,
        httponly=COOKIE_NO_JS_ACCESS,
        secure=COOKIE_SECURE_MODE,
        samesite=COOKIE_SAMESITE_POLICY,
    )
    return db_user


@router.post("/logout/")
async def logout(
    response: Response,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    crud.deactivate_session(db=db, access_token=access_token)
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out."}


@router.post("/users/", response_model=schemas.User)
async def create_user(
    username: str = Body(...),
    email: str = Body(...),
    password: str = Body(...),
    display_name: str = Body(...),
    bio: Optional[str] = Body(None),
    avatar_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    try:
        new_user = schemas.UserCreate(
            username=username,
            email=email,
            password=password,
            display_name=display_name,
            bio=bio,
            avatar_file=avatar_file,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user.",
        ) from e
    return crud.create_user(db=db, user=new_user)


@router.get("/users/me/", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(get_current_user),
):
    return current_user


@router.patch("/users/me/", response_model=schemas.User)
async def update_user_profile(
    username: Optional[str] = Body(None),
    email: Optional[str] = Body(None),
    password: Optional[str] = Body(None),
    display_name: Optional[str] = Body(None),
    bio: Optional[str] = Body(None),
    avatar_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        user_data = schemas.UserProfileUpdate(
            username=username,
            email=email,
            password=password,
            display_name=display_name,
            bio=bio,
            avatar_file=avatar_file,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user.",
        ) from e
    return crud.update_user_profile(
        db=db, user=user_data, existing_user=current_user
    )


@router.patch("/users/{username}/role/", response_model=schemas.User)
async def update_user_role(
    username: str,
    new_role: enums.UserRole,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_or_moderator),
):
    return crud.update_user_role(db=db, username=username, new_role=new_role)
