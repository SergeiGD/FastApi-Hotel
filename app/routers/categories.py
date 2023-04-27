from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Body, Form
from typing import Annotated
from schemas.categories import Category, CategoryCreateForm, CategoryUpdateForm
from dependencies import get_db
from hotel_business_module.gateways.categories_gateway import CategoriesGateway
from hotel_business_module.models.categories import Category as DbCategory
from sqlalchemy.orm import Session
from utils import raise_not_fount, update_model_fields, convert_form_data

router = APIRouter(
    prefix='/categories',
    tags=['categories', ],
)

db_depends = Annotated[Session, Depends(get_db)]


@router.get('/', response_model=list[Category])
def get_categories(db: db_depends):
    return CategoriesGateway.get_all(db)


@router.get('/{category_id}', response_model=Category)
def get_category(category_id: int, db: db_depends):
    db_category = CategoriesGateway.get_by_id(category_id, db)
    if db_category is None:
        raise_not_fount(DbCategory.REPR_MODEL_NAME)
    return db_category


@router.post('/', response_model=Category)
def create_category(category: Annotated[CategoryCreateForm, Depends()], photo: UploadFile, db: db_depends):
    category = category.convert_to_model()
    try:
        db_category = DbCategory(**category.dict())
        CategoriesGateway.save_category(
            category=db_category,
            file=photo.file,
            file_name=photo.filename,
            db=db
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_category


@router.put('/{category_id}', response_model=Category)
def edit_tag(
        category_id: int,
        category: Annotated[CategoryUpdateForm, Depends()],
        db: db_depends,
        photo: UploadFile | None = None,
):
    db_category = CategoriesGateway.get_by_id(category_id, db)
    if db_category is None:
        raise_not_fount(DbCategory.REPR_MODEL_NAME)

    category = category.convert_to_model()
    try:
        update_model_fields(db_category, category.dict())
        CategoriesGateway.save_category(
            category=db_category,
            file=photo.file if photo is not None else None,
            file_name=photo.filename if photo is not None else None,
            db=db
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_category


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(category_id: int, db: db_depends):
    db_category = CategoriesGateway.get_by_id(category_id, db)
    if db_category is not None:
        CategoriesGateway.delete_category(db_category, db)
