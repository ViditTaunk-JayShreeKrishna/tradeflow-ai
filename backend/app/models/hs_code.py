from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class HSCode(Base):
    __tablename__ = "hs_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)  # e.g. "8471.30"
    chapter = Column(String(2), nullable=False, index=True)              # "84"
    heading = Column(String(4), nullable=True, index=True)               # "8471"
    description = Column(Text, nullable=False)
    level = Column(Integer, nullable=False)     # 2=chapter, 4=heading, 6=subheading, 8=tariff
    parent_code = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    duty_rates = relationship("DutyRate", back_populates="hs_code")
    products = relationship("Product", back_populates="hs_code")
    shipment_items = relationship("ShipmentItem", back_populates="hs_code")

    def __repr__(self):
        return f"<HSCode {self.code} - {self.description[:40]}>"