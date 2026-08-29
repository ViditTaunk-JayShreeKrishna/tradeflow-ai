from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app.models.country import Country


class CountryOut(BaseModel):
    code: str
    name: str
    currency_code: str
    region: str
    model_config = {"from_attributes": True}


router = APIRouter(prefix="/countries", tags=["Countries"])


@router.get("/", response_model=List[CountryOut])
async def get_countries(db: Session = Depends(get_db)):
    return db.query(Country).filter(
        Country.is_active == True
    ).order_by(Country.name).all()