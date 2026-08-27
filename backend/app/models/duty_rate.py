import enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Date, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class DutySource(str, enum.Enum):
    WTO_MFN = "wto_mfn"          # Most Favoured Nation rate
    FTA = "fta"                    # Free Trade Agreement rate
    MANUAL = "manual"              # Manually entered
    INDIA_CUSTOMS = "india_customs"


class DutyRate(Base):
    __tablename__ = "duty_rates"

    id = Column(Integer, primary_key=True, index=True)
    hs_code_id = Column(Integer, ForeignKey("hs_codes.id"), nullable=False, index=True)
    importing_country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)

    # NULL means this is the general MFN rate (applies to all exporters)
    exporting_country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)

    basic_duty_rate = Column(Float, default=0.0)          # % basic customs duty
    additional_duty_rate = Column(Float, default=0.0)     # % anti-dumping / safeguard
    igst_rate = Column(Float, default=0.0)                # % IGST (for India)
    cess_rate = Column(Float, default=0.0)                # % cess (for India)

    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    source = Column(Enum(DutySource), default=DutySource.MANUAL)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    hs_code = relationship("HSCode", back_populates="duty_rates")
    importing_country = relationship(
        "Country", foreign_keys=[importing_country_id],
        back_populates="import_duties"
    )

    def total_rate(self):
        return self.basic_duty_rate + self.additional_duty_rate + self.igst_rate + self.cess_rate

    def __repr__(self):
        return f"<DutyRate HS:{self.hs_code_id} → Country:{self.importing_country_id} {self.basic_duty_rate}%>"