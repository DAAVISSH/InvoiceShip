from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
import io

def generate_invoice_pdf(invoice) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=15*mm, leftMargin=15*mm,
                            topMargin=15*mm, bottomMargin=15*mm)

    styles = getSampleStyleSheet()
    elements = []

    # Header
    right_style = ParagraphStyle("right", fontSize=10, alignment=TA_RIGHT,
                                  textColor=colors.HexColor("#7F8C8D"))
    title_right_style = ParagraphStyle("title_right", fontSize=24, alignment=TA_RIGHT,
                                        textColor=colors.HexColor("#2C3E50"),
                                        fontName="Helvetica-Bold")

    sender_info = f"""<b>{invoice.sender_name}</b><br/>
{invoice.sender_email}<br/>
{invoice.sender_address or ''}"""

    due_date_line = f"Due Date: {invoice.due_date}" if invoice.due_date else ""

    header_data = [
        [Paragraph(sender_info, styles["Normal"]), Paragraph("INVOICE", title_right_style)],
        [Paragraph("", styles["Normal"]), Paragraph(f"Invoice #: {invoice.invoice_number}", right_style)],
        [Paragraph("", styles["Normal"]), Paragraph(f"Date: {invoice.created_at.strftime('%B %d, %Y')}", right_style)],
        [Paragraph("", styles["Normal"]), Paragraph(due_date_line, right_style)],
    ]

    header_table = Table(header_data, colWidths=[110*mm, 70*mm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))

    # Client info
    info_data = [
        [Paragraph("<b>Bill To:</b>", styles["Normal"])],
        [Paragraph(invoice.client_name, styles["Normal"])],
        [Paragraph(invoice.client_email, styles["Normal"])],
        [Paragraph(invoice.client_address or "", styles["Normal"])],
    ]
    info_table = Table(info_data, colWidths=[180*mm])
    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8*mm))

    # Items table
    item_data = [["Description", "Qty", "Unit Price", "Total"]]
    for item in invoice.items:
        item_data.append([
            item["description"],
            str(item["quantity"]),
            f"{invoice.currency} {item['unit_price']:.2f}",
            f"{invoice.currency} {item['quantity'] * item['unit_price']:.2f}"
        ])

    items_table = Table(item_data, colWidths=[100*mm, 20*mm, 35*mm, 35*mm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 6*mm))

    # Totals
    totals_data = [
        ["Subtotal:", f"{invoice.currency} {invoice.subtotal:.2f}"],
        [f"Tax ({invoice.tax_percent}%):", f"{invoice.currency} {invoice.tax_amount:.2f}"],
        ["Total:", f"{invoice.currency} {invoice.total:.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[145*mm, 35*mm])
    totals_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (2, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 2), (-1, 2), 12),
        ("LINEABOVE", (0, 2), (-1, 2), 1, colors.HexColor("#2C3E50")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(totals_table)

    # Notes
    if invoice.notes:
        elements.append(Spacer(1, 8*mm))
        elements.append(Paragraph("<b>Notes:</b>", styles["Normal"]))
        elements.append(Paragraph(invoice.notes, styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()