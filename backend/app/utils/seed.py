from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    Country, HSCode, DutyRate, FreightRate,
    ExchangeRate, DutySource, FreightMode
)


# ─── DATA ────────────────────────────────────────────────────────────────────

COUNTRIES = [
    {"code": "IN", "code3": "IND", "name": "India",          "currency_code": "INR", "currency_name": "Indian Rupee",     "region": "Asia"},
    {"code": "CN", "code3": "CHN", "name": "China",          "currency_code": "CNY", "currency_name": "Chinese Yuan",     "region": "Asia"},
    {"code": "US", "code3": "USA", "name": "United States",  "currency_code": "USD", "currency_name": "US Dollar",        "region": "North America"},
    {"code": "AE", "code3": "ARE", "name": "UAE",            "currency_code": "AED", "currency_name": "UAE Dirham",       "region": "Middle East"},
    {"code": "DE", "code3": "DEU", "name": "Germany",        "currency_code": "EUR", "currency_name": "Euro",             "region": "Europe"},
    {"code": "GB", "code3": "GBR", "name": "United Kingdom", "currency_code": "GBP", "currency_name": "British Pound",    "region": "Europe"},
    {"code": "JP", "code3": "JPN", "name": "Japan",          "currency_code": "JPY", "currency_name": "Japanese Yen",     "region": "Asia"},
    {"code": "SG", "code3": "SGP", "name": "Singapore",      "currency_code": "SGD", "currency_name": "Singapore Dollar", "region": "Asia"},
    {"code": "AU", "code3": "AUS", "name": "Australia",      "currency_code": "AUD", "currency_name": "Australian Dollar","region": "Oceania"},
    {"code": "BR", "code3": "BRA", "name": "Brazil",         "currency_code": "BRL", "currency_name": "Brazilian Real",   "region": "South America"},
    {"code": "ZA", "code3": "ZAF", "name": "South Africa",   "currency_code": "ZAR", "currency_name": "South African Rand","region": "Africa"},
    {"code": "FR", "code3": "FRA", "name": "France",         "currency_code": "EUR", "currency_name": "Euro",             "region": "Europe"},
    {"code": "CA", "code3": "CAN", "name": "Canada",         "currency_code": "CAD", "currency_name": "Canadian Dollar",  "region": "North America"},
    {"code": "KR", "code3": "KOR", "name": "South Korea",    "currency_code": "KRW", "currency_name": "South Korean Won", "region": "Asia"},
    {"code": "TH", "code3": "THA", "name": "Thailand",       "currency_code": "THB", "currency_name": "Thai Baht",        "region": "Asia"},
]

HS_CODES = [
    # Textiles
    {"code": "61",       "chapter": "61", "heading": None,   "level": 2, "description": "Articles of apparel and clothing accessories, knitted or crocheted"},
    {"code": "6109",     "chapter": "61", "heading": "6109", "level": 4, "description": "T-shirts, singlets and other vests, knitted or crocheted"},
    {"code": "6109.10",  "chapter": "61", "heading": "6109", "level": 6, "description": "T-shirts of cotton, knitted or crocheted"},
    # Electronics
    {"code": "84",       "chapter": "84", "heading": None,   "level": 2, "description": "Nuclear reactors, boilers, machinery and mechanical appliances"},
    {"code": "8471",     "chapter": "84", "heading": "8471", "level": 4, "description": "Automatic data processing machines (computers)"},
    {"code": "8471.30",  "chapter": "84", "heading": "8471", "level": 6, "description": "Portable automatic data processing machines (laptops)"},
    {"code": "85",       "chapter": "85", "heading": None,   "level": 2, "description": "Electrical machinery and equipment"},
    {"code": "8517",     "chapter": "85", "heading": "8517", "level": 4, "description": "Telephone sets, including smartphones"},
    {"code": "8517.12",  "chapter": "85", "heading": "8517", "level": 6, "description": "Smartphones and mobile phones"},
    # Pharmaceuticals
    {"code": "30",       "chapter": "30", "heading": None,   "level": 2, "description": "Pharmaceutical products"},
    {"code": "3004",     "chapter": "30", "heading": "3004", "level": 4, "description": "Medicaments for therapeutic or prophylactic uses"},
    {"code": "3004.90",  "chapter": "30", "heading": "3004", "level": 6, "description": "Other medicaments for retail sale"},
    # Gems and Jewelry (India major export)
    {"code": "71",       "chapter": "71", "heading": None,   "level": 2, "description": "Natural or cultured pearls, precious stones and metals"},
    {"code": "7113",     "chapter": "71", "heading": "7113", "level": 4, "description": "Articles of jewellery and parts thereof"},
    {"code": "7113.19",  "chapter": "71", "heading": "7113", "level": 6, "description": "Articles of jewellery of other precious metals"},
]

DUTY_RATES = [
    # India importing laptops (8471.30)
    {"hs_code": "8471.30", "importing": "IN", "basic": 0.0,  "igst": 18.0, "cess": 0.0, "source": DutySource.INDIA_CUSTOMS},
    # India importing smartphones (8517.12)
    {"hs_code": "8517.12", "importing": "IN", "basic": 0.0,  "igst": 18.0, "cess": 0.0, "source": DutySource.INDIA_CUSTOMS},
    # India importing t-shirts (6109.10)
    {"hs_code": "6109.10", "importing": "IN", "basic": 20.0, "igst": 5.0,  "cess": 0.0, "source": DutySource.INDIA_CUSTOMS},
    # India importing medicines (3004.90)
    {"hs_code": "3004.90", "importing": "IN", "basic": 10.0, "igst": 12.0, "cess": 0.0, "source": DutySource.INDIA_CUSTOMS},
    # USA importing laptops
    {"hs_code": "8471.30", "importing": "US", "basic": 0.0,  "igst": 0.0,  "cess": 0.0, "source": DutySource.WTO_MFN},
    # USA importing textiles
    {"hs_code": "6109.10", "importing": "US", "basic": 16.5, "igst": 0.0,  "cess": 0.0, "source": DutySource.WTO_MFN},
    # UAE importing electronics
    {"hs_code": "8517.12", "importing": "AE", "basic": 5.0,  "igst": 0.0,  "cess": 0.0, "source": DutySource.WTO_MFN},
    # Germany importing jewellery
    {"hs_code": "7113.19", "importing": "DE", "basic": 2.5,  "igst": 0.0,  "cess": 0.0, "source": DutySource.WTO_MFN},
]

FREIGHT_RATES = [
    # Sea rates (per 20GP container in USD)
    {"origin": "IN", "dest": "US", "mode": FreightMode.SEA, "container": "20GP", "rate": 2800.0},
    {"origin": "IN", "dest": "US", "mode": FreightMode.SEA, "container": "40GP", "rate": 4200.0},
    {"origin": "CN", "dest": "US", "mode": FreightMode.SEA, "container": "20GP", "rate": 2200.0},
    {"origin": "IN", "dest": "DE", "mode": FreightMode.SEA, "container": "20GP", "rate": 1800.0},
    {"origin": "IN", "dest": "AE", "mode": FreightMode.SEA, "container": "20GP", "rate": 650.0},
    {"origin": "IN", "dest": "GB", "mode": FreightMode.SEA, "container": "20GP", "rate": 2100.0},
    {"origin": "CN", "dest": "DE", "mode": FreightMode.SEA, "container": "20GP", "rate": 2500.0},
    {"origin": "IN", "dest": "AU", "mode": FreightMode.SEA, "container": "20GP", "rate": 1900.0},
    # Air rates (per kg in USD)
    {"origin": "IN", "dest": "US", "mode": FreightMode.AIR, "container": None, "rate": 5.8},
    {"origin": "IN", "dest": "AE", "mode": FreightMode.AIR, "container": None, "rate": 1.9},
    {"origin": "IN", "dest": "DE", "mode": FreightMode.AIR, "container": None, "rate": 4.2},
    {"origin": "CN", "dest": "US", "mode": FreightMode.AIR, "container": None, "rate": 4.5},
]

EXCHANGE_RATES = [
    {"base": "USD", "target": "INR", "rate": 83.5},
    {"base": "USD", "target": "CNY", "rate": 7.24},
    {"base": "USD", "target": "EUR", "rate": 0.92},
    {"base": "USD", "target": "GBP", "rate": 0.79},
    {"base": "USD", "target": "AED", "rate": 3.67},
    {"base": "USD", "target": "JPY", "rate": 149.2},
    {"base": "USD", "target": "SGD", "rate": 1.34},
    {"base": "USD", "target": "AUD", "rate": 1.53},
    {"base": "USD", "target": "BRL", "rate": 4.97},
    {"base": "USD", "target": "ZAR", "rate": 18.63},
    {"base": "USD", "target": "CAD", "rate": 1.36},
    {"base": "USD", "target": "KRW", "rate": 1325.0},
    {"base": "USD", "target": "THB", "rate": 35.1},
]


# ─── SEEDER ──────────────────────────────────────────────────────────────────

def seed():
    db: Session = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(Country).count() > 0:
            print("✓ Database already seeded. Skipping.")
            return

        print("Seeding countries...")
        country_map = {}
        for c in COUNTRIES:
            country = Country(**c)
            db.add(country)
            db.flush()
            country_map[c["code"]] = country
        print(f"  ✓ {len(COUNTRIES)} countries added")

        print("Seeding HS codes...")
        hs_map = {}
        for h in HS_CODES:
            hs = HSCode(**h)
            db.add(hs)
            db.flush()
            hs_map[h["code"]] = hs
        print(f"  ✓ {len(HS_CODES)} HS codes added")

        print("Seeding duty rates...")
        for d in DUTY_RATES:
            duty = DutyRate(
                hs_code_id=hs_map[d["hs_code"]].id,
                importing_country_id=country_map[d["importing"]].id,
                basic_duty_rate=d["basic"],
                igst_rate=d["igst"],
                cess_rate=d["cess"],
                source=d["source"],
                is_active=True,
            )
            db.add(duty)
        print(f"  ✓ {len(DUTY_RATES)} duty rates added")

        print("Seeding freight rates...")
        today = date.today()
        for f in FREIGHT_RATES:
            freight = FreightRate(
                origin_country_id=country_map[f["origin"]].id,
                destination_country_id=country_map[f["dest"]].id,
                mode=f["mode"],
                container_type=f["container"],
                rate_usd=f["rate"],
                unit="container" if f["mode"] == FreightMode.SEA else "kg",
                effective_date=today,
                source="manual_seed",
            )
            db.add(freight)
        print(f"  ✓ {len(FREIGHT_RATES)} freight rates added")

        print("Seeding exchange rates...")
        today = date.today()
        for e in EXCHANGE_RATES:
            rate = ExchangeRate(
                base_currency=e["base"],
                target_currency=e["target"],
                rate=e["rate"],
                date=today,
            )
            db.add(rate)
        print(f"  ✓ {len(EXCHANGE_RATES)} exchange rates added")

        db.commit()
        print("\n✅ Database seeded successfully!")

    except Exception as ex:
        db.rollback()
        print(f"\n❌ Seeding failed: {ex}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()