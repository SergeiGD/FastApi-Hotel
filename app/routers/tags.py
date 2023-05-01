from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.tags import Tag, TagCreate, TagUpdate
from sqlalchemy.orm import Session
from dependencies import get_db, PermissionsDependency
from hotel_business_module.gateways.tags_gateway import TagsGateway
from hotel_business_module.models.tags import Tag as DbTag
from utils import update_model_fields, raise_not_fount
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/tags',
    tags=['tags', ],
)


@router.get('/', response_model=list[Tag])
def get_tags(db: Session = Depends(get_db)):
    return TagsGateway.get_all(db)


@router.get('/{tag_id}', response_model=Tag)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = TagsGateway.get_by_id(tag_id, db)
    if db_tag is None:
        raise_not_fount(DbTag.REPR_MODEL_NAME)
    return db_tag


@router.post('/', response_model=Tag, status_code=status.HTTP_201_CREATED)
def create_tag(
        tag: TagCreate,
        access: Annotated[None, Depends(PermissionsDependency(['add_tag']))],
        db: Session = Depends(get_db),
):
    try:
        db_tag = DbTag(**tag.dict())
        TagsGateway.save_tag(db_tag, db)
    except ValueError as err:
        logger.info(f'ошибка создания тега {tag.name}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_tag


@router.put('/{tag_id}', response_model=Tag)
def edit_tag(
        tag_id: int,
        tag: TagUpdate,
        access: Annotated[None, Depends(PermissionsDependency(['edit_tag']))],
        db: Session = Depends(get_db),
):
    db_tag = TagsGateway.get_by_id(tag_id, db)
    if db_tag is None:
        raise_not_fount(DbTag.REPR_MODEL_NAME)

    try:
        update_model_fields(db_tag, tag.dict())
        TagsGateway.save_tag(db_tag, db)
    except ValueError as err:
        logger.info(f'ошибка сохранения тега {tag_id}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_tag


@router.delete('/{tag_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
        tag_id: int,
        access: Annotated[None, Depends(PermissionsDependency(['delete_tag']))],
        db: Session = Depends(get_db),
):
    db_tag = TagsGateway.get_by_id(tag_id, db)
    if db_tag is not None:
        TagsGateway.delete_tag(db_tag, db)
