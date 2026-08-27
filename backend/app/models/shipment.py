import enum
from sqlalchemy import (
    Column, Integer, String, Float, Text,
    DateTime, Date, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ShipmentStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    IN_TRANSIT = "in_transit"
    CUSTOMS = "customs"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class TransportMode(str, enum.Enum):
    SEA = "sea"
    AIR = "air"
    ROAD = "road"
    RAIL = "rail"


class Incoterm(str, enum.Enum):
    EXW = "EXW"
    FCA = "FCA"
    FOB = "FOB"
    CFR = "CFR"
    CIF = "CIF"
    DAP = "DAP"
    DDP = "DDP"


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    origin_country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    destination_country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)

    reference_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.DRAFT, index=True)
    mode_of_transport = Column(Enum(TransportMode), default=TransportMode.SEA)
    incoterm = Column(Enum(Incoterm), default=Incoterm.FOB)

    estimated_departure = Column(Date, nullable=True)
    estimated_arrival = Column(Date, nullable=True)
    actual_departure = Column(Date, nullable=True)
    actual_arrival = Column(Date, nullable=True)

    total_value = Column(Float, nullable=True)
    currency_code = Column(String(3), default="USD")
    total_weight_kg = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="shipments")
    origin_country = relationship(
        "Country", foreign_keys=[origin_country_id],
        back_populates="origin_shipments"
    )
    destination_country = relationship(
        "Country", foreign_keys=[destination_country_id],
        back_populates="destination_shipments"
    )
    items = relationship("ShipmentItem", back_populates="shipment", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="shipment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Shipment {self.reference_number} [{self.status}]>"


class ShipmentItem(Base):
    __tablename__ = "shipment_items"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    hs_code_id = Column(Integer, ForeignKey("hs_codes.id"), nullable=True)

    description = Column(String(300), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_of_measure = Column(String(20), default="piece")
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shipment = relationship("Shipment", back_populates="items")
    product = relationship("Product", back_populates="shipment_items")
    hs_code = relationship("HSCode", back_populates="shipment_items")

    def __repr__(self):
        return f"<ShipmentItem {self.description} qty:{self.quantity}>"