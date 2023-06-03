from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.permissions import Permission
from sqlalchemy.orm import Session
from dependencies import get_db, PermissionsDependency
from hotel_business_module.gateways.permissions_gateway import PermissionsGateway
from hotel_business_module.models.permissions import Permission as DbPermission
from utils import update_model_fields, raise_not_fount
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/permissions',
    tags=['permissions', ],
)


@router.get(
    '/',
    response_model=list[Permission],
    dependencies=[Depends(PermissionsDependency(['show_permission']))],
)
def get_permissions(db: Session = Depends(get_db)):
    return PermissionsGateway.get_all(db)


@router.get(
    '/{permission_id}',
    response_model=Permission,
    dependencies=[Depends(PermissionsDependency(['show_permission']))],
)
def get_tag(permission_id: int, db: Session = Depends(get_db)):
    db_permission = PermissionsGateway.get_by_id(permission_id, db)
    if db_permission is None:
        logger.warning(f'Разрешение с id {permission_id} не найдено')
        raise_not_fount(DbPermission.REPR_MODEL_NAME)
    return db_permission
