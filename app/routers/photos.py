from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from typing import Annotated
from schemas.photos import Photo, PhotosCreateForm, PhotosUpdateForm
from dependencies import get_db, PermissionsDependency
from hotel_business_module.gateways.photos_gateway import PhotosGateway
from hotel_business_module.models.photos import Photo as DbPhoto
from sqlalchemy.orm import Session
from utils import raise_not_fount, update_model_fields
import logging
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/photos',
    tags=['photos', ],
)


@router.get('/', response_model=list[Photo])
def get_photos(db: Session = Depends(get_db)):
    return PhotosGateway.get_all(db)


@router.get('/{photo_id}', response_model=Photo)
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    db_photo = PhotosGateway.get_by_id(photo_id, db)
    if db_photo is None:
        logger.warning(f'Фото с id {photo_id} не найдено')
        raise_not_fount(DbPhoto.REPR_MODEL_NAME)
    return db_photo


@router.post(
    '/',
    response_model=Photo,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionsDependency(['create_photo', 'edit_category']))],
)
async def create_photo(
        photo: Annotated[PhotosCreateForm, Depends()],
        photo_file: UploadFile,
        db: Session = Depends(get_db),
):
    schema_photo = photo.convert_to_model()  # получаем модель pydantic
    try:
        db_photo = DbPhoto(**schema_photo.dict())
        await PhotosGateway.asave_photo(
            photo=db_photo,
            file=photo_file,
            file_name=photo_file.filename,
            db=db
        )
    except ValueError as err:
        logger.info(f'Ошибка создания фотографии. {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_photo


@router.patch(
    '/{photo_id}',
    response_model=Photo,
    dependencies=[Depends(PermissionsDependency(['edit_photo', 'edit_category']))],
)
async def edit_photo(
        photo_id: int,
        photo: Annotated[PhotosUpdateForm, Depends()],
        db: Session = Depends(get_db),
        photo_file: UploadFile | None = None,
):
    db_photo = PhotosGateway.get_by_id(photo_id, db)
    if db_photo is None:
        raise_not_fount(DbPhoto.REPR_MODEL_NAME)

    schema_photo = photo.convert_to_model(db_photo)  # получаем модель pydantic
    try:
        update_model_fields(db_photo, schema_photo.dict())  # обновляем поля
        await PhotosGateway.asave_photo(
            photo=db_photo,
            file=photo_file,
            file_name=photo_file.filename if photo_file is not None else None,
            db=db
        )
    except ValueError as err:
        logger.info(f'Ошибка сохранения фото. id - {photo_id}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_photo


@router.delete(
    '/{photo_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionsDependency(['delete_photo', 'edit_category']))],
)
def delete_photo(
        photo_id: int,
        db: Session = Depends(get_db),
):
    db_photo = PhotosGateway.get_by_id(photo_id, db)
    if db_photo is not None:
        PhotosGateway.delete_photo(db_photo, db)
