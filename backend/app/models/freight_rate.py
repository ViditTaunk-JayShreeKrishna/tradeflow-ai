import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FreightMode(str, enum.Enum):
    SEA = "sea"
    AIR = "air"


class FreightRate(Base):
    __tablename__ = "freight_rates"

    id = Column(Integer, primary_key=True, index=True)
    origin_country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    destination_country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)

    mode = Column(Enum(FreightMode), nullable=False, index=True)
    container_type = Column(String(10), nullable=True)   # 20GP, 40GP, 40HC for sea
    rate_usd = Column(Float, nullable=False)              # Rate in USD
    unit = Column(String(20), default="container")        # container, kg, cbm
    effective_date = Column(Date, nullable=False, index=True)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    origin_country = relationship(
        "Country", foreign_keys=[origin_country_id],
        back_populates="origin_freight"
    )
    destination_country = relationship(
        "Country", foreign_keys=[destination_country_id],
        back_populates="destination_freight"
    )

    def __repr__(self):
        return f"<FreightRate {self.origin_country_id}→{self.destination_country_id} ${self.rate_usd}>"