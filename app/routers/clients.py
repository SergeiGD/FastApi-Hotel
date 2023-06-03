from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import get_db, PermissionsDependency
from schemas.clients import Client, ClientCreate, ClientUpdate
from hotel_business_module.gateways.clients_gateway import ClientsGateway
from hotel_business_module.models.users import Client as DbClient
from sqlalchemy.orm import Session
from utils import raise_not_fount, update_model_fields
import logging
from logger_conf import LOGGING as LOG_CONF


logging.config.dictConfig(LOG_CONF)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/clients',
    tags=['clients', ],
)


@router.get('/', response_model=list[Client], dependencies=[Depends(PermissionsDependency(['show_client']))],)
def get_clients(db: Session = Depends(get_db)):
    return ClientsGateway.get_all(db)


@router.get('/{client_id}', response_model=Client, dependencies=[Depends(PermissionsDependency(['show_client']))],)
def get_client(client_id: int, db: Session = Depends(get_db)):
    db_client = ClientsGateway.get_by_id(client_id, db)
    if db_client is None:
        logger.warning(f'Клиент с id {client_id} не найден')
        raise_not_fount(DbClient.REPR_MODEL_NAME)
    return db_client


@router.post(
    '/',
    response_model=Client,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(PermissionsDependency(['add_client']))],
)
def create_client(
        client: ClientCreate,
        db: Session = Depends(get_db),
):
    try:
        db_client = DbClient(**client.dict())
        ClientsGateway.save_client(db_client, db)
    except ValueError as err:
        logger.warning(f'Ошибка создания клиента {client.email}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_client


@router.put('/{client_id}', response_model=Client, dependencies=[Depends(PermissionsDependency(['edit_client']))],)
def edit_client(
        client_id: int,
        client: ClientUpdate,
        db: Session = Depends(get_db),
):
    db_client = ClientsGateway.get_by_id(client_id, db)
    if db_client is None:
        raise_not_fount(DbClient.REPR_MODEL_NAME)

    try:
        update_model_fields(db_client, client.dict())
        ClientsGateway.save_client(db_client, db)
    except ValueError as err:
        logger.info(f'Ошибка сохранения клиента {client_id}, {str(err)}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    return db_client


@router.delete(
    '/{client_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionsDependency(['edit_client']))],
)
def delete_client(
        client_id: int,
        db: Session = Depends(get_db),
):
    db_client = ClientsGateway.get_by_id(client_id, db)
    if db_client is not None:
        ClientsGateway.delete_client(db_client, db)
