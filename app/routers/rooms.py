from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.rooms import Room, RoomCreate, RoomUpdate
from sqlalchemy.orm import Session
from dependencies import get_db, PermissionsDependency
from hotel_business_module.gateways.rooms_gateway import RoomsGateway
from hotel_business_module.gateways.categories_gateway import CategoriesGateway
from hotel_business_module.models.rooms import Room as DbRoom
from hotel_business_module.models.categories import Category as DbCategory
from utils import raise_not_fount, update_model_fields
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/rooms',
    tags=['rooms', ],
)


@router.get('/', response_model=list[Room])
def get_rooms(db: Session = Depends(get_db)):
    return RoomsGateway.get_all(db)


@router.get('/{room_id}', response_model=Room)
def get_room(room_id: int, db: Session = Depends(get_db)):
    db_room = RoomsGateway.get_by_id(room_id, db)
    if db_room is None:
        logger.warning(f'Комната с id {room_id} не найдена')
        raise_not_fount(DbRoom.REPR_MODEL_NAME)
    return db_room


@router.post('/', response_model=Room, status_code=status.HTTP_201_CREATED)
def create_room(
        room: RoomCreate,
        access: Annotated[None, Depends(PermissionsDependency(['add_room']))],
        db: Session = Depends(get_db),
):
    db_category = CategoriesGateway.get_by_id(room.category_id, db)
    logger.debug(f'попытка создание комнаты для категории {room.category_id}')
    if db_category is None:
        raise_not_fount(DbCategory.REPR_MODEL_NAME)

    try:
        db_room = DbRoom(**room.dict(), category=db_category)
        RoomsGateway.save_room(db_room, db)
    except ValueError as err:
        logger.warning(f'Ошибка создания комнаты. номер - {room.room_number}, категория {room.category_id}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_room


@router.put('/{room_id}', response_model=Room)
def edit_room(
        room_id: int,
        room: RoomUpdate,
        access: Annotated[None, Depends(PermissionsDependency(['edit_room']))],
        db: Session = Depends(get_db)
):
    db_room = RoomsGateway.get_by_id(room_id, db)
    if db_room is None:
        raise_not_fount(DbRoom.REPR_MODEL_NAME)

    try:
        update_model_fields(db_room, room.dict())
        RoomsGateway.save_room(db_room, db)
    except ValueError as err:
        logger.warning(f'Ошибка сохранения комнаты. id - {room_id}, категория {db_room.category_id}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_room


@router.delete('/{room_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
        room_id: int,
        access: Annotated[None, Depends(PermissionsDependency(['delete_room']))],
        db: Session = Depends(get_db),
):
    db_room = RoomsGateway.get_by_id(room_id, db)
    if db_room is not None:
        logger.warning(f'Комната с id {room_id} не найдена')
        RoomsGateway.delete_room(db_room, db)
