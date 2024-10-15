from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from thinga import models, schemas, crud
from thinga.dependencies import get_db, get_current_user, get_admin_or_moderator

router = APIRouter()


@router.get("/images/random/", response_model=list[schemas.Image])
async def get_random_images(
    db: models.Session = Depends(get_db),
):
    return crud.get_two_random_images(db=db)


@router.get("/images/{image_id}/", response_model=schemas.Image)
async def read_image(
    image_id: int,
    db: Session = Depends(get_db),
):
    db_image = crud.get_image_by_id(db=db, image_id=image_id)
    if db_image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found.",
        )
    return db_image


@router.post("/images/", response_model=schemas.Image)
async def upload_image(
    media_file: UploadFile = File(None),
    alt_text: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_admin_or_moderator),
):
    new_image = schemas.ImageCreate(media_file=media_file, alt_text=alt_text)
    return crud.create_image(db=db, image=new_image)


@router.delete("/images/{image_id}/")
async def delete_image(
    image_id: int,
    db: models.Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_or_moderator),
):
    crud.delete_image(db=db, image_id=image_id)
    return {"message": "Image deleted successfully."}


@router.post("/images/{image_id}/rate/", response_model=schemas.Image)
async def rate_image(
    image_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.update_image_score(db=db, image_id=image_id)
