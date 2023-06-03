from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from typing import Annotated
from schemas.categories import Category, CategoryCreateForm, CategoryUpdateForm
from schemas.tags import Tag
from dependencies import get_db, PermissionsDependency
from hotel_business_module.gateways.categories_gateway import CategoriesGateway
from hotel_business_module.gateways.tags_gateway import TagsGateway
from hotel_business_module.models.categories import Category as DbCategory
from hotel_business_module.models.tags import Tag as DbTag
from sqlalchemy.orm import Session
from utils import raise_not_fount, update_model_fields
import logging
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/categories',
    tags=['categories', ],
)

db_depends = Annotated[Session, Depends(get_db)]


def filter_params_dependency(
        page_size: int = 8, page: int = 1, desc: bool = False, show_hidden: bool = False, sort_by: str = 'id',
        id: int | None = None, name: str | None = None, beds_from: int | None = None, beds_until: int | None = None,
        floors_from: int | None = None, floors_until: int | None = None,
        square_from: int | None = None, square_until: int | None = None,
        price_from: int | None = None, price_until: int | None = None,
        rooms_from: int | None = None, rooms_until: int | None = None,
):
    # получение параметров фильтрации для списка категорий
    return {field: val for field, val in locals().items() if val is not None}


@router.get('/', response_model=list[Category])
def get_categories(filter: Annotated[dict, Depends(filter_params_dependency)], db: db_depends):
    logger.debug(f'поиск категорий с фильтром - {filter}')
    items, pages_count = CategoriesGateway.filter(filter=filter, db=db)
    pagination_info = {
        'pages_count': pages_count,
        'current_page': filter.get('page', 1),
    }
    json_data = jsonable_encoder([pagination_info, *parse_obj_as(list[Category], items)])
    return JSONResponse(content=json_data)


@router.get('/{category_id}', response_model=Category)
def get_category(category_id: int, db: db_depends):
    db_category = CategoriesGateway.get_by_id(category_id, db)
    if db_category is None:
        logger.warning(f'Категория с id {category_id} не найдена')
        raise_not_fount(DbCategory.REPR_MODEL_NAME)
    return db_category


@router.get('/{category_id}/familiar', response_model=list[Category])
def get_familiar(category_id: int, db: db_depends):
    db_category = CategoriesGateway.get_by_id(category_id, db)
    if db_category is None:
        logger.warning(f'Категория с id {category_id} не найдена')
        raise_not_fount(DbCategory.REPR_MODEL_NAME)
    return CategoriesGateway.get_familiar(db_category, db)


@router.post('/', response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
        category: Annotated[CategoryCreateForm, Depends()],
        photo: UploadFile,
        db: db_depends,
        access: Annotated[None, Depends(PermissionsDependency(['add_category']))],
):
    schema_category = category.convert_to_model()  # получаем модель pydantic
    try:
        db_category = DbCategory(**schema_category.dict())
        await CategoriesGateway.asave_category(
            category=db_category,
            file=photo,
            file_name=photo.filename,
            db=db
        )
    except ValueError as err:
        logger.info(f'Ошибка создания категории. {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_category


@router.put('/{category_id}', response_model=Category)
async def edit_category(
        category_id: int,
        category: Annotated[CategoryUpdateForm, Depends()],
        db: db_depends,
        access: Annotated[None, Depends(PermissionsDependency(['edit_category']))],
        photo: UploadFile | None = None,
):
    db_category = CategoriesGateway.get_by_id(category_id, db)
    if db_category is None:
        raise_not_fount(DbCategory.REPR_MODEL_NAME)

    schema_category = category.convert_to_model(db_category)  # получаем модель pydantic
    try:
        update_model_fields(db_category, schema_category.dict())  # обновляем поля
        await CategoriesGateway.asave_category(
            category=db_category,
            file=photo,
            file_name=photo.filename if photo is not None else None,
            db=db
        )
    except ValueError as err:
        logger.info(f'Ошибка сохрарения категории. id - {category_id}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_category


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
        category_id: int, 
        db: db_depends, 
        access: Annotated[None, Depends(PermissionsDependency(['delete_category']))],
):
    db_category = CategoriesGateway.get_by_id(category_id, db)
    if db_category is not None:
        CategoriesGateway.delete_category(db_category, db)


@router.get('/{category_id}/tags', response_model=list[Tag])
def get_tags(category_id: int, db: db_depends):
    db_category = CategoriesGateway.get_by_id(category_id, db)
    if db_category is None:
        raise_not_fount(DbCategory.REPR_MODEL_NAME)
    return db_category.tags


@router.put('/{category_id}/tags', response_model=Tag)
def add_tag(
        category_id: int,
        tag_id: Annotated[int, Body(embed=True)],
        db: db_depends,
        access: Annotated[None, Depends(PermissionsDependency(['edit_category', 'edit_tag']))],
):
    logger.debug(f'попытка добавления тега {tag_id} к категории {category_id}')
    db_category = CategoriesGateway.get_by_id(category_id, db)
    if db_category is None:
        logger.warning(f'Категория с id {category_id} не найдена')
        raise_not_fount(DbCategory.REPR_MODEL_NAME)
    db_tag = TagsGateway.get_by_id(tag_id, db)
    if db_tag is None:
        logger.warning(f'Тег с id {tag_id} не найден')
        raise_not_fount(DbTag.REPR_MODEL_NAME)

    CategoriesGateway.add_tag_to_category(db_category, db_tag, db)
    return db_tag


@router.delete('/{category_id}/tags', status_code=status.HTTP_204_NO_CONTENT)
def remove_tag(
        category_id: int,
        tag_id: Annotated[int, Body(embed=True)],
        db: db_depends,
        access: Annotated[None, Depends(PermissionsDependency(['edit_category', 'edit_tag']))],
):
    logger.debug(f'попытка удаления тега {tag_id} из категории {category_id}')
    db_category = CategoriesGateway.get_by_id(category_id, db)
    db_tag = TagsGateway.get_by_id(tag_id, db)
    if db_category is not None and db_tag is not None:
        CategoriesGateway.remove_tag_from_category(db_category, db_tag, db)
