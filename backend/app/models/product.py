from sqlalchemy import (
    Column, Integer, String, Float,
    DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    hs_code_id = Column(Integer, ForeignKey("hs_codes.id"), nullable=True)

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    hs_code_confidence = Column(Float, nullable=True)  # ML confidence score 0-1
    unit_of_measure = Column(String(20), default="piece")  # kg, piece, mt, litre
    unit_price = Column(Float, nullable=True)
    currency_code = Column(String(3), default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="products")
    hs_code = relationship("HSCode", back_populates="products")
    shipment_items = relationship("ShipmentItem", back_populates="product")

    def __repr__(self):
        return f"<Product {self.name}>"