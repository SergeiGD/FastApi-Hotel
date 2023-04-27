from fastapi import APIRouter, Depends
from schemas.rooms import Room
from sqlalchemy.orm import Session
from dependencies import get_db
from hotel_business_module.gateways.rooms_gateway import RoomsGateway


router = APIRouter(
    prefix='/rooms',
    tags=['rooms', ],
)


@router.get('/', response_model=list[Room])
def get_rooms(db: Session = Depends(get_db)):
    rooms = RoomsGateway.get_all(db)
    print(rooms)
    return rooms
