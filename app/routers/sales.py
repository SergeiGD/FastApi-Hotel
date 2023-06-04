from fastapi import APIRouter, Depends, UploadFile, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from typing import Annotated
from schemas.sales import Sale, SaleCreateForm, SaleUpdateForm
from dependencies import get_db, PermissionsDependency
from hotel_business_module.gateways.sales_gateway import SalesGateway
from hotel_business_module.models.sales import Sale as DbSale
from sqlalchemy.orm import Session
from utils import raise_not_fount, update_model_fields
import logging
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/sales',
    tags=['sales', ],
)


@router.get('/', response_model=list[Sale])
def get_sales(db: Session = Depends(get_db)):
    return SalesGateway.get_all(db)


@router.get('/{sale_id}', response_model=Sale)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = SalesGateway.get_by_id(sale_id, db)
    if db_sale is None:
        logger.warning(f'Скидка с id {sale_id} не найдена')
        raise_not_fount(DbSale.REPR_MODEL_NAME)
    return db_sale


@router.post(
    '/',
    response_model=Sale,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionsDependency(['create_sale']))],
)
async def create_sale(
        sale: Annotated[SaleCreateForm, Depends()],
        photo: UploadFile,
        db: Session = Depends(get_db),
):
    schema_sale = sale.convert_to_model()  # получаем модель pydantic
    try:
        db_sale = DbSale(**schema_sale.dict())
        await SalesGateway.asave_sale(
            sale=db_sale,
            file=photo,
            file_name=photo.filename,
            db=db
        )
    except ValueError as err:
        logger.info(f'Ошибка создания скидки. {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_sale


@router.patch(
    '/{sale_id}',
    response_model=Sale,
    dependencies=[Depends(PermissionsDependency(['edit_sale']))],
)
async def edit_sale(
        sale_id: int,
        category: Annotated[SaleUpdateForm, Depends()],
        db: Session = Depends(get_db),
        photo: UploadFile | None = None,
):
    db_sale = SalesGateway.get_by_id(sale_id, db)
    if db_sale is None:
        raise_not_fount(DbSale.REPR_MODEL_NAME)

    schema_sale = category.convert_to_model(db_sale)  # получаем модель pydantic
    try:
        update_model_fields(db_sale, schema_sale.dict())  # обновляем поля
        await SalesGateway.asave_sale(
            sale=db_sale,
            file=photo,
            file_name=photo.filename if photo is not None else None,
            db=db
        )
    except ValueError as err:
        logger.info(f'Ошибка сохранения скидки. id - {sale_id}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_sale


@router.delete(
    '/{sale_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionsDependency(['delete_sale']))],
)
def delete_category(
        sale_id: int,
        db: Session = Depends(get_db),
):
    db_sale = SalesGateway.get_by_id(sale_id, db)
    if db_sale is not None:
        SalesGateway.delete_sale(db_sale, db)
