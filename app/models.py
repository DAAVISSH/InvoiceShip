from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON
from datetime import datetime
from app.database import Base
import enum

class InvoiceStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    paid = "paid"

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, nullable=False)
    
    # Client details
    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False)
    client_address = Column(String, nullable=True)
    
    # Sender details
    sender_name = Column(String, nullable=False)
    sender_email = Column(String, nullable=False)
    sender_address = Column(String, nullable=True)
    
    # Invoice details
    items = Column(JSON, nullable=False)
    tax_percent = Column(Float, default=0.0)
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    currency = Column(String, default="EUR")
    notes = Column(String, nullable=True)
    
    # Status and dates
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.draft)
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(String, nullable=True)