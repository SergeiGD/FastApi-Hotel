from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Body
from schemas.groups import Group, GroupCreate, GroupUpdate
from schemas.permissions import Permission
from sqlalchemy.orm import Session
from dependencies import get_db, PermissionsDependency
from hotel_business_module.gateways.groups_gateway import GroupsGateway
from hotel_business_module.gateways.permissions_gateway import PermissionsGateway
from hotel_business_module.models.groups import Group as DbGroup
from hotel_business_module.models.permissions import Permission as DbPermission
from utils import update_model_fields, raise_not_fount
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/groups',
    tags=['groups', ],
)


@router.get('/', response_model=list[Group], dependencies=[Depends(PermissionsDependency(['show_group']))],)
def get_groups(db: Session = Depends(get_db)):
    return GroupsGateway.get_all(db)


@router.get('/{group_id}', response_model=Group, dependencies=[Depends(PermissionsDependency(['show_group']))],)
def get_group(group_id: int, db: Session = Depends(get_db)):
    db_group = GroupsGateway.get_by_id(group_id, db)
    if db_group is None:
        logger.warning(f'Группа с id {group_id} не найден')
        raise_not_fount(DbGroup.REPR_MODEL_NAME)
    return db_group


@router.post(
    '/', response_model=Group,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionsDependency(['add_group']))],
)
def create_group(
        group: GroupCreate,
        db: Session = Depends(get_db),
):
    try:
        db_group = DbGroup(**group.dict())
        GroupsGateway.save_group(db_group, db)
    except ValueError as err:
        logger.warning(f'Ошибка создания группы {group.name}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_group


@router.put('/{group_id}', response_model=Group, dependencies=[Depends(PermissionsDependency(['edit_group']))],)
def edit_group(
        group_id: int,
        group: GroupUpdate,
        db: Session = Depends(get_db),
):
    db_group = GroupsGateway.get_by_id(group_id, db)
    if db_group is None:
        logger.warning(f'Группа с id {group_id} не найден')
        raise_not_fount(DbGroup.REPR_MODEL_NAME)

    try:
        update_model_fields(db_group, group.dict())
        GroupsGateway.save_group(db_group, db)
    except ValueError as err:
        logger.info(f'Ошибка сохранения группы {group_id}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_group


@router.delete(
    '/{group_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionsDependency(['delete_group']))],
)
def delete_group(
        group_id: int,
        db: Session = Depends(get_db),
):
    db_group = GroupsGateway.get_by_id(group_id, db)
    if db_group is not None:
        GroupsGateway.delete_group(db_group, db)


@router.get(
    '/{group_id}/permissions',
    response_model=list[Permission],
    dependencies=[Depends(PermissionsDependency(['show_group', 'show_permissions']))]
)
def get_permissions(group_id: int, db: Session = Depends(get_db)):
    db_group = GroupsGateway.get_by_id(group_id, db)
    if db_group is None:
        logger.warning(f'Группа с id {group_id} не найдена')
        raise_not_fount(DbGroup.REPR_MODEL_NAME)
    return db_group.permissions


@router.put(
    '/{group_id}/permissions',
    response_model=Permission,
    dependencies=[Depends(PermissionsDependency(['edit_group']))]
)
def add_permission(
        group_id: int,
        permission_id: Annotated[int, Body(embed=True)],
        db: Session = Depends(get_db),
):
    db_group = GroupsGateway.get_by_id(group_id, db)
    if db_group is None:
        logger.warning(f'Группа с id {group_id} не найден')
        raise_not_fount(DbGroup.REPR_MODEL_NAME)
    db_permission = PermissionsGateway.get_by_id(permission_id, db)
    if db_permission is None:
        logger.warning(f'Разрешение с id {permission_id} не найдено')
        raise_not_fount(DbPermission.REPR_MODEL_NAME)

    GroupsGateway.add_permission_to_group(db_group, db_permission, db)
    return db_permission


@router.delete(
    '/{group_id}/permissions',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionsDependency(['edit_group']))]
)
def remove_permission(
        group_id: int,
        permission_id: Annotated[int, Body(embed=True)],
        db: Session = Depends(get_db),
):
    db_group = GroupsGateway.get_by_id(group_id, db)
    db_permission = PermissionsGateway.get_by_id(permission_id, db)
    if db_group is not None and db_permission is not None:
        GroupsGateway.remove_permission_from_group(db_group, db_permission, db)
