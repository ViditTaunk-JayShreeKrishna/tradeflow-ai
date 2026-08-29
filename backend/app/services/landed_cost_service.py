from sqlalchemy.orm import Session
from typing import Optional
from app.models import Country, HSCode, DutyRate, FreightRate, ExchangeRate
from app.schemas.landed_cost import LandedCostRequest, LandedCostResponse, CostBreakdownItem

INSURANCE_RATE = 0.005          # 0.5% of FOB
DEFAULT_SEA_FREIGHT_USD = 1500.0
DEFAULT_AIR_FREIGHT_PER_KG = 5.0
DEFAULT_WEIGHT_KG = 100.0


def calculate_landed_cost(request: LandedCostRequest, db: Session) -> LandedCostResponse:

    # ── 1. Fetch countries ────────────────────────────────────────────────────
    origin = db.query(Country).filter(
        Country.code == request.origin_country_code.upper()
    ).first()
    destination = db.query(Country).filter(
        Country.code == request.destination_country_code.upper()
    ).first()

    if not origin:
        raise ValueError(f"Origin country '{request.origin_country_code}' not found")
    if not destination:
        raise ValueError(f"Destination country '{request.destination_country_code}' not found")

    # ── 2. Fetch HS code ──────────────────────────────────────────────────────
    hs_record = db.query(HSCode).filter(HSCode.code == request.hs_code).first()
    hs_description = hs_record.description if hs_record else "Description not available"

    # ── 3. Fetch duty rates ───────────────────────────────────────────────────
    duty_rate = None
    if hs_record:
        duty_rate = db.query(DutyRate).filter(
            DutyRate.hs_code_id == hs_record.id,
            DutyRate.importing_country_id == destination.id,
            DutyRate.is_active == True,
        ).first()

    duty_rate_found = duty_rate is not None
    basic_duty_rate = duty_rate.basic_duty_rate if duty_rate else 0.0
    additional_duty_rate = duty_rate.additional_duty_rate if duty_rate else 0.0
    igst_rate = duty_rate.igst_rate if duty_rate else 0.0
    cess_rate = duty_rate.cess_rate if duty_rate else 0.0
    duty_source = duty_rate.source.value if duty_rate else "not_found"

    # ── 4. Fetch freight rate ─────────────────────────────────────────────────
    freight_record = db.query(FreightRate).filter(
        FreightRate.origin_country_id == origin.id,
        FreightRate.destination_country_id == destination.id,
        FreightRate.mode == request.transport_mode,
    ).order_by(FreightRate.effective_date.desc()).first()

    freight_rate_found = freight_record is not None
    weight_kg = request.weight_kg or DEFAULT_WEIGHT_KG
    num_containers = request.num_containers or 1

    if freight_record:
        if request.transport_mode == "air":
            freight_usd = freight_record.rate_usd * weight_kg
        else:
            freight_usd = freight_record.rate_usd * num_containers
        freight_source = freight_record.source or "database"
    else:
        freight_usd = (
            DEFAULT_AIR_FREIGHT_PER_KG * weight_kg
            if request.transport_mode == "air"
            else DEFAULT_SEA_FREIGHT_USD * num_containers
        )
        freight_source = "estimated_default"

    # ── 5. Calculate costs ────────────────────────────────────────────────────
    fob = request.fob_value_usd
    insurance_usd = fob * INSURANCE_RATE
    cif = fob + freight_usd + insurance_usd

    basic_duty_usd = cif * basic_duty_rate / 100
    additional_duty_usd = cif * additional_duty_rate / 100

    # IGST base = CIF + basic duty + additional duty
    igst_base = cif + basic_duty_usd + additional_duty_usd
    igst_usd = igst_base * igst_rate / 100

    # Cess base = CIF + basic duty
    cess_base = cif + basic_duty_usd
    cess_usd = cess_base * cess_rate / 100

    total = fob + freight_usd + insurance_usd + basic_duty_usd + additional_duty_usd + igst_usd + cess_usd
    per_unit = total / request.quantity

    # ── 6. Currency conversion ────────────────────────────────────────────────
    local_currency = destination.currency_code
    fx = db.query(ExchangeRate).filter(
        ExchangeRate.base_currency == "USD",
        ExchangeRate.target_currency == local_currency,
    ).order_by(ExchangeRate.date.desc()).first()

    exchange_rate = fx.rate if fx else 1.0
    total_local = total * exchange_rate
    per_unit_local = per_unit * exchange_rate

    # ── 7. Build breakdown ────────────────────────────────────────────────────
    def item(label, amount, desc, rate=None):
        pct = (amount / total * 100) if total > 0 else 0
        rate_str = f" ({rate}%)" if rate is not None else ""
        return CostBreakdownItem(
            label=label,
            amount_usd=round(amount, 2),
            amount_local=round(amount * exchange_rate, 2),
            local_currency=local_currency,
            percentage_of_total=round(pct, 1),
            description=desc + rate_str,
        )

    breakdown = [
        item("FOB Value",       fob,                "Product value at port of origin"),
        item("Freight",         freight_usd,         f"{'Sea' if request.transport_mode == 'sea' else 'Air'} freight charges"),
        item("Insurance",       insurance_usd,        "Cargo insurance (0.5% of FOB)"),
        item("Basic Duty",      basic_duty_usd,       "Basic customs duty on CIF value", basic_duty_rate),
        item("Additional Duty", additional_duty_usd,  "Anti-dumping / safeguard duty", additional_duty_rate),
        item("IGST / VAT",      igst_usd,             "Integrated GST or VAT on import", igst_rate),
        item("Cess",            cess_usd,             "Social welfare surcharge", cess_rate),
    ]

    return LandedCostResponse(
        hs_code=request.hs_code,
        hs_description=hs_description,
        origin_country=origin.name,
        destination_country=destination.name,
        transport_mode=request.transport_mode,
        fob_value_usd=round(fob, 2),
        quantity=request.quantity,
        freight_usd=round(freight_usd, 2),
        insurance_usd=round(insurance_usd, 2),
        cif_value_usd=round(cif, 2),
        basic_duty_usd=round(basic_duty_usd, 2),
        additional_duty_usd=round(additional_duty_usd, 2),
        igst_usd=round(igst_usd, 2),
        cess_usd=round(cess_usd, 2),
        total_landed_cost_usd=round(total, 2),
        per_unit_landed_cost_usd=round(per_unit, 4),
        basic_duty_rate=basic_duty_rate,
        additional_duty_rate=additional_duty_rate,
        igst_rate=igst_rate,
        cess_rate=cess_rate,
        local_currency_code=local_currency,
        exchange_rate_to_usd=exchange_rate,
        total_landed_cost_local=round(total_local, 2),
        per_unit_landed_cost_local=round(per_unit_local, 4),
        breakdown=breakdown,
        freight_source=freight_source,
        duty_source=duty_source,
        duty_rate_found=duty_rate_found,
        freight_rate_found=freight_rate_found,
    )