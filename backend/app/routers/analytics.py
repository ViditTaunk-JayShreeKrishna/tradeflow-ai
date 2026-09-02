from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import Country, HSCode, DutyRate, FreightRate, ExchangeRate
from app.schemas.analytics import (
    OverviewStats, FreightRateData,
    ExchangeRateData, DutyRateData
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewStats)
def get_overview(db: Session = Depends(get_db)):
    last_fx = db.query(ExchangeRate).order_by(
        ExchangeRate.date.desc()
    ).first()

    return OverviewStats(
        total_countries=db.query(func.count(Country.id)).scalar(),
        total_hs_codes=db.query(func.count(HSCode.id)).scalar(),
        total_duty_rates=db.query(func.count(DutyRate.id)).filter(
            DutyRate.is_active == True
        ).scalar(),
        total_freight_routes=db.query(func.count(FreightRate.id)).scalar(),
        supported_currencies=db.query(
            func.count(func.distinct(ExchangeRate.target_currency))
        ).scalar(),
        last_forex_update=str(last_fx.date) if last_fx else None,
    )


@router.get("/freight-rates", response_model=List[FreightRateData])
def get_freight_rates(db: Session = Depends(get_db)):
    OriginCountry = aliased(Country)
    DestCountry = aliased(Country)

    rows = db.query(
        FreightRate,
        OriginCountry.code.label("origin_code"),
        OriginCountry.name.label("origin_name"),
        DestCountry.code.label("dest_code"),
        DestCountry.name.label("dest_name"),
    ).join(
        OriginCountry, FreightRate.origin_country_id == OriginCountry.id
    ).join(
        DestCountry, FreightRate.destination_country_id == DestCountry.id
    ).order_by(FreightRate.mode, FreightRate.rate_usd).all()

    return [
        FreightRateData(
            route=f"{r.origin_code}→{r.dest_code}",
            route_full=f"{r.origin_name} → {r.dest_name}",
            mode=r.FreightRate.mode.value,
            rate_usd=r.FreightRate.rate_usd,
            container_type=r.FreightRate.container_type,
            unit=r.FreightRate.unit,
        )
        for r in rows
    ]


@router.get("/exchange-rates", response_model=List[ExchangeRateData])
def get_exchange_rates(db: Session = Depends(get_db)):
    latest_date = db.query(
        func.max(ExchangeRate.date)
    ).filter(ExchangeRate.base_currency == "USD").scalar()

    if not latest_date:
        return []

    rates = db.query(ExchangeRate).filter(
        ExchangeRate.base_currency == "USD",
        ExchangeRate.date == latest_date,
    ).order_by(ExchangeRate.rate.asc()).all()

    return [
        ExchangeRateData(
            currency=r.target_currency,
            rate=r.rate,
            date=str(r.date),
        )
        for r in rates
    ]


@router.get("/duty-rates", response_model=List[DutyRateData])
def get_duty_rates(db: Session = Depends(get_db)):
    rows = db.query(
        DutyRate,
        HSCode.code.label("hs_code"),
        Country.code.label("country_code"),
        Country.name.label("country_name"),
    ).join(
        HSCode, DutyRate.hs_code_id == HSCode.id
    ).join(
        Country, DutyRate.importing_country_id == Country.id
    ).filter(DutyRate.is_active == True).all()

    return [
        DutyRateData(
            hs_code=r.hs_code,
            country=r.country_name,
            country_code=r.country_code,
            basic_duty=r.DutyRate.basic_duty_rate,
            igst=r.DutyRate.igst_rate,
            additional_duty=r.DutyRate.additional_duty_rate,
            total_rate=r.DutyRate.basic_duty_rate + r.DutyRate.igst_rate + r.DutyRate.additional_duty_rate,
        )
        for r in rows
    ]