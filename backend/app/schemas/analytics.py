from pydantic import BaseModel
from typing import List, Optional


class OverviewStats(BaseModel):
    total_countries: int
    total_hs_codes: int
    total_duty_rates: int
    total_freight_routes: int
    supported_currencies: int
    last_forex_update: Optional[str] = None


class FreightRateData(BaseModel):
    route: str
    route_full: str
    mode: str
    rate_usd: float
    container_type: Optional[str] = None
    unit: str


class ExchangeRateData(BaseModel):
    currency: str
    rate: float
    date: Optional[str] = None


class DutyRateData(BaseModel):
    hs_code: str
    country: str
    country_code: str
    basic_duty: float
    igst: float
    additional_duty: float
    total_rate: float