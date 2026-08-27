from sqlalchemy import Column, Integer, String, Float, DateTime, Date, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String(3), nullable=False, index=True)    # USD
    target_currency = Column(String(3), nullable=False, index=True)  # INR
    rate = Column(Float, nullable=False)
    date = Column(Date, nullable=False, index=True)
    source = Column(String(50), default="exchangerate-api")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("base_currency", "target_currency", "date", name="uq_rate_per_day"),
    )

    def __repr__(self):
        return f"<ExchangeRate {self.base_currency}/{self.target_currency} = {self.rate} on {self.date}>"