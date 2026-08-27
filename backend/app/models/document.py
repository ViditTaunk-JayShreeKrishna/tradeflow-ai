import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class DocumentType(str, enum.Enum):
    COMMERCIAL_INVOICE = "commercial_invoice"
    PACKING_LIST = "packing_list"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    BILL_OF_LADING = "bill_of_lading"
    CUSTOMS_DECLARATION = "customs_declaration"


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    SENT = "sent"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    document_type = Column(Enum(DocumentType), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)

    generated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shipment = relationship("Shipment", back_populates="documents")
    user = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.document_type} [{self.status}]>"