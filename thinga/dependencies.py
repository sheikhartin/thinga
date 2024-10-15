from typing import Iterator

from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session

from thinga import models, crud, utils
from thinga.database import SessionLocal


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_access_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return access_token


async def get_current_user(
    request: Request,
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
) -> models.User:
    client_fingerprint = utils.generate_client_fingerprint(request)
    db_session = crud.verify_session(
        db=db,
        access_token=access_token,
        client_fingerprint=client_fingerprint,
    )
    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )

    db_user = crud.get_user_by_id(db=db, user_id=db_session.user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    return db_user
