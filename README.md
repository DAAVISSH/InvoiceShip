# InvoiceShip

A backend API that generates professional PDF invoices and delivers them directly to clients via email, fully automated with a single API call.

Built for freelancers, agencies, and small businesses that need a clean invoicing system without manual work.

---

## What It Does

- Creates professional PDF invoices with auto-generated invoice numbers
- Calculates subtotals, tax, and totals automatically
- Sends invoices directly to client email with PDF attached
- Tracks invoice status — draft, sent, paid
- Stores full invoice history in PostgreSQL
- Full REST API with Swagger documentation

---

## Tech Stack

- **Python 3.13**
- **FastAPI** — REST API framework
- **PostgreSQL + SQLAlchemy** — invoice storage
- **ReportLab** — PDF generation
- **SMTP / Gmail** — email delivery
- **Docker** — containerized deployment

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/invoiceship.git
cd invoiceship
```

### 2. Set up environment variables

Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/invoicedb
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_FROM=your_gmail@gmail.com
```

For Gmail, use an App Password — generate one at https://myaccount.google.com/apppasswords

### 3. Create the database
```bash
psql -U postgres
CREATE DATABASE invoicedb;
\q
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the API
```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the full Swagger UI.

---

## API Endpoints

| Method |       Endpoint        | Description                      |
|--------|-----------------------|----------------------------------|
| POST   | /invoices/            | Create a new invoice             |
| GET    | /invoices/            | List all invoices                |
| GET    | /invoices/{id}        | Get single invoice               |
| DELETE | /invoices/{id}        | Delete invoice                   |
| PATCH  | /invoices/{id}/status | Update invoice status            |
| GET    | /invoices/{id}/pdf    | Download invoice as PDF          |
| POST   | /invoices/{id}/send   | Generate PDF and email to client |

---

## Creating an Invoice
```json
POST /invoices/
{
  "client_name": "John Smith",
  "client_email": "john@example.com",
  "client_address": "123 Main Street, Berlin, Germany",
  "sender_name": "Your Name",
  "sender_email": "you@example.com",
  "sender_address": "Dubai, UAE",
  "items": [
    {
      "description": "Backend API Development",
      "quantity": 10,
      "unit_price": 28.00
    }
  ],
  "tax_percent": 21,
  "currency": "EUR",
  "notes": "Payment due within 30 days.",
  "due_date": "2026-03-27"
}
```

---

## Invoice Status Flow
```
draft → sent → paid
```

Update status via PATCH /invoices/{id}/status with body:
```json
{ "status": "paid" }
```

---

## Docker
```bash
docker build -t invoiceship .
docker run -p 8000:8000 --env-file .env invoiceship
```