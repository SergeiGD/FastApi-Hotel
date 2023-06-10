from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from dependencies import get_db, PermissionsDependency
from schemas.workers import Worker, WorkerCreate, WorkerUpdate
from schemas.groups import Group
from hotel_business_module.gateways.workers_gateway import WorkersGateway
from hotel_business_module.gateways.groups_gateway import GroupsGateway
from hotel_business_module.models.users import Worker as DbWorker
from hotel_business_module.models.groups import Group as DbGroup
from sqlalchemy.orm import Session
from utils import raise_not_fount, update_model_fields
import logging
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/workers',
    tags=['workers', ],
)


@router.get('/', response_model=list[Worker], dependencies=[Depends(PermissionsDependency(['show_worker']))],)
def get_workers(db: Session = Depends(get_db)):
    return WorkersGateway.get_all(db)


@router.get('/{worker_id}', response_model=Worker, dependencies=[Depends(PermissionsDependency(['show_worker']))],)
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    db_worker = WorkersGateway.get_by_id(worker_id, db)
    if db_worker is None:
        logger.warning(f'Сотрудник с id {worker_id} не найден')
        raise_not_fount(DbWorker.REPR_MODEL_NAME)
    return db_worker


@router.post(
    '/',
    response_model=Worker,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionsDependency(['show_worker']))],
)
def create_worker(
        worker: WorkerCreate,
        db: Session = Depends(get_db),
):
    try:
        db_worker = DbWorker(**worker.dict())
        WorkersGateway.save_worker(db_worker, db)
    except ValueError as err:
        logger.warning(f'Ошибка создания сотрудника {worker.email}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_worker


@router.put('/{worker_id}', response_model=Worker, dependencies=[Depends(PermissionsDependency(['edit_worker']))],)
def edit_worker(
        worker_id: int,
        worker: WorkerUpdate,
        db: Session = Depends(get_db),
):
    db_worker = WorkersGateway.get_by_id(worker_id, db)
    if db_worker is None:
        raise_not_fount(DbWorker.REPR_MODEL_NAME)

    try:
        update_model_fields(db_worker, worker.dict())
        WorkersGateway.save_worker(db_worker, db)
    except ValueError as err:
        logger.info(f'Ошибка сохранения сотрудника {worker_id}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_worker


@router.delete(
    '/{worker_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionsDependency(['edit_worker']))],
)
def delete_worker(
        worker_id: int,
        db: Session = Depends(get_db),
):
    db_worker = WorkersGateway.get_by_id(worker_id, db)
    if db_worker is not None:
        WorkersGateway.delete_worker(db_worker, db)


@router.get(
    '/{worker_id}/groups',
    response_model=list[Group],
    dependencies=[Depends(PermissionsDependency(['show_worker', 'show_group']))]
)
def get_groups(worker_id: int, db: Session = Depends(get_db)):
    db_worker = WorkersGateway.get_by_id(worker_id, db)
    if db_worker is None:
        logger.warning(f'Сотрудник с id {worker_id} не найден')
        raise_not_fount(DbWorker.REPR_MODEL_NAME)
    return db_worker.groups


@router.put(
    '/{worker_id}/groups',
    response_model=Group,
    dependencies=[Depends(PermissionsDependency(['edit_worker', 'edit_group']))]
)
def add_group(
        worker_id: int,
        group_id: Annotated[int, Body(embed=True)],
        db: Session = Depends(get_db),
):
    db_worker = WorkersGateway.get_by_id(worker_id, db)
    if db_worker is None:
        logger.warning(f'Сотрудник с id {worker_id} не найден')
        raise_not_fount(DbWorker.REPR_MODEL_NAME)
    db_group = GroupsGateway.get_by_id(group_id, db)
    if db_group is None:
        logger.warning(f'Группа с id {group_id} не найдена')
        raise_not_fount(DbGroup.REPR_MODEL_NAME)

    WorkersGateway.add_group_to_worker(db_worker, db_group, db)
    return db_group


@router.delete(
    '/{worker_id}/groups',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionsDependency(['edit_worker', 'edit_group']))]
)
def remove_group(
        worker_id: int,
        group_id: Annotated[int, Body(embed=True)],
        db: Session = Depends(get_db),
):
    db_worker = WorkersGateway.get_by_id(worker_id, db)
    db_group = GroupsGateway.get_by_id(group_id, db)
    if db_worker is not None and db_group is not None:
        WorkersGateway.remove_group_from_worker(db_worker, db_group, db)
