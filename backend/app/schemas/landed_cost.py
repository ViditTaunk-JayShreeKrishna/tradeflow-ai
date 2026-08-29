from pydantic import BaseModel
from typing import Optional, List


class LandedCostRequest(BaseModel):
    hs_code: str
    origin_country_code: str
    destination_country_code: str
    fob_value_usd: float
    quantity: float
    unit_of_measure: str = "piece"
    transport_mode: str = "sea"        # "sea" or "air"
    weight_kg: Optional[float] = None  # required for air
    num_containers: Optional[int] = 1  # for sea


class CostBreakdownItem(BaseModel):
    label: str
    amount_usd: float
    amount_local: float
    local_currency: str
    percentage_of_total: float
    description: str


class LandedCostResponse(BaseModel):
    hs_code: str
    hs_description: str
    origin_country: str
    destination_country: str
    transport_mode: str
    fob_value_usd: float
    quantity: float
    freight_usd: float
    insurance_usd: float
    cif_value_usd: float
    basic_duty_usd: float
    additional_duty_usd: float
    igst_usd: float
    cess_usd: float
    total_landed_cost_usd: float
    per_unit_landed_cost_usd: float
    basic_duty_rate: float
    additional_duty_rate: float
    igst_rate: float
    cess_rate: float
    local_currency_code: str
    exchange_rate_to_usd: float
    total_landed_cost_local: float
    per_unit_landed_cost_local: float
    breakdown: List[CostBreakdownItem]
    freight_source: str
    duty_source: str
    duty_rate_found: bool
    freight_rate_found: bool