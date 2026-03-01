from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Invoice, InvoiceStatus
from app.pdf_generator import generate_invoice_pdf
from app.email_sender import send_invoice_email
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random

router = APIRouter()

class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float

class InvoiceCreate(BaseModel):
    client_name: str
    client_email: str
    client_address: Optional[str] = None
    sender_name: str
    sender_email: str
    sender_address: Optional[str] = None
    items: List[InvoiceItem]
    tax_percent: Optional[float] = 0.0
    currency: Optional[str] = "EUR"
    notes: Optional[str] = None
    due_date: Optional[str] = None

class StatusUpdate(BaseModel):
    status: InvoiceStatus

def generate_invoice_number():
    year = datetime.utcnow().year
    random_part = random.randint(1000, 9999)
    return f"INV-{year}-{random_part}"

@router.post("/")
def create_invoice(data: InvoiceCreate, db: Session = Depends(get_db)):
    items = [item.dict() for item in data.items]
    subtotal = sum(item["quantity"] * item["unit_price"] for item in items)
    tax_amount = round(subtotal * data.tax_percent / 100, 2)
    total = round(subtotal + tax_amount, 2)

    invoice = Invoice(
        invoice_number=generate_invoice_number(),
        client_name=data.client_name,
        client_email=data.client_email,
        client_address=data.client_address,
        sender_name=data.sender_name,
        sender_email=data.sender_email,
        sender_address=data.sender_address,
        items=items,
        tax_percent=data.tax_percent,
        subtotal=round(subtotal, 2),
        tax_amount=tax_amount,
        total=total,
        currency=data.currency,
        notes=data.notes,
        due_date=data.due_date
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice

@router.get("/")
def get_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()

@router.get("/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.patch("/{invoice_id}/status")
def update_status(invoice_id: int, data: StatusUpdate, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.status = data.status
    db.commit()
    return {"message": f"Status updated to {data.status}"}

@router.get("/{invoice_id}/pdf")
def download_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    pdf_bytes = generate_invoice_pdf(invoice)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_number}.pdf"}
    )

@router.post("/{invoice_id}/send")
def send_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    pdf_bytes = generate_invoice_pdf(invoice)
    try:
        send_invoice_email(
            to_email=invoice.client_email,
            client_name=invoice.client_name,
            invoice_number=invoice.invoice_number,
            pdf_bytes=pdf_bytes
        )
        invoice.status = InvoiceStatus.sent
        db.commit()
        return {"message": f"Invoice sent to {invoice.client_email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted"}