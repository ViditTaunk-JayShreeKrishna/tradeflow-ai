from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(2), unique=True, nullable=False, index=True)   # IN, US, CN
    code3 = Column(String(3), unique=True, nullable=False)               # IND, USA, CHN
    name = Column(String(100), nullable=False)
    currency_code = Column(String(3), nullable=False)                    # INR, USD, CNY
    currency_name = Column(String(50))
    region = Column(String(50))                                          # Asia, Europe, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    origin_shipments = relationship(
        "Shipment", foreign_keys="Shipment.origin_country_id",
        back_populates="origin_country"
    )
    destination_shipments = relationship(
        "Shipment", foreign_keys="Shipment.destination_country_id",
        back_populates="destination_country"
    )
    import_duties = relationship(
        "DutyRate", foreign_keys="DutyRate.importing_country_id",
        back_populates="importing_country"
    )
    origin_freight = relationship(
        "FreightRate", foreign_keys="FreightRate.origin_country_id",
        back_populates="origin_country"
    )
    destination_freight = relationship(
        "FreightRate", foreign_keys="FreightRate.destination_country_id",
        back_populates="destination_country"
    )

    def __repr__(self):
        return f"<Country {self.code} - {self.name}>"