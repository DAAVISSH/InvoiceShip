from fastapi import FastAPI
from app.database import engine, Base
from app.routes import invoices

Base.metadata.create_all(bind=engine)

app = FastAPI(title="InvoiceShip")

app.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])

@app.get("/")
def root():
    return {"message": "Invoice Generator API is running"}