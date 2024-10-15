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

from thinga import models, schemas, crud, utils
from thinga.dependencies import get_db, get_access_token, get_current_user
from thinga.config import DEBUG_ENABLED

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
        httponly=True,
        secure=False if DEBUG_ENABLED else True,
        samesite="lax",
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
    avatar_file: UploadFile = File(None),
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
