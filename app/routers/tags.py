from fastapi import APIRouter, Depends
from schemas.tags import Tag
from sqlalchemy.orm import Session
from dependencies import get_db
from hotel_business_module.gateways.tags_gateway import TagsGateway


router = APIRouter(
    prefix='/tags',
    tags=['tags', ],
)


@router.get('/', response_model=list[Tag])
def get_tags(db: Session = Depends(get_db)):
    tags = TagsGateway.get_all(db)
    return tags
