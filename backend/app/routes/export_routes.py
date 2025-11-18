"""
API routes for exporting data (PDF, CSV).
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import List, Optional
import io
import csv
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

router = APIRouter(prefix="/api/v1/export", tags=["Export"])


class RouteExportRequest(BaseModel):
    """Request model for route export."""
    route: List[dict]
    user_name: str
    total_time: float
    total_score: float
    companies_visited: int
    event_name: str = "UH Engineering Career Fair"


@router.post("/route-pdf")
async def export_route_pdf(request: RouteExportRequest):
    """
    Export route itinerary as PDF.

    Args:
        request: Route export request

    Returns:
        PDF file download
    """
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="PDF generation not available. Install reportlab: pip install reportlab"
        )

    # Create PDF in memory
    buffer = io.BytesIO()

    # Create document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1  # Center
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20,
        alignment=1
    )

    # Title
    elements.append(Paragraph(request.event_name, title_style))
    elements.append(Paragraph(f"Personalized Itinerary for {request.user_name}", subtitle_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Summary section
    summary_data = [
        ['Total Companies:', str(request.companies_visited)],
        ['Total Time:', f'{request.total_time:.1f} minutes'],
        ['Total Score:', f'{request.total_score:.1f}'],
        ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M')]
    ]

    summary_table = Table(summary_data, colWidths=[2 * inch, 3 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.5 * inch))

    # Route table header
    elements.append(Paragraph("Your Optimized Route", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))

    # Route table
    route_data = [['#', 'Booth', 'Arrival Time', 'Travel', 'Service', 'Score']]

    cumulative_time = 0
    for i, stop in enumerate(request.route, 1):
        arrival_min = int(stop['arrival_time'])
        route_data.append([
            str(i),
            stop['booth_number'],
            f"{arrival_min} min",
            f"{stop['travel_time']:.1f} min",
            f"{stop['service_time']:.1f} min",
            f"{stop['score']:.1f}"
        ])

    route_table = Table(route_data, colWidths=[0.5*inch, 1*inch, 1.2*inch, 1*inch, 1*inch, 1*inch])
    route_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90E2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
    ]))

    elements.append(route_table)

    # Build PDF
    doc.build(elements)

    # Seek to beginning
    buffer.seek(0)

    # Return as downloadable file
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=itinerary_{request.user_name.replace(' ', '_')}.pdf"
        }
    )


@router.post("/route-csv")
async def export_route_csv(request: RouteExportRequest):
    """
    Export route itinerary as CSV.

    Args:
        request: Route export request

    Returns:
        CSV file download
    """
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Career Fair Itinerary'])
    writer.writerow([f'User: {request.user_name}'])
    writer.writerow([f'Event: {request.event_name}'])
    writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'])
    writer.writerow([])

    # Write summary
    writer.writerow(['Summary'])
    writer.writerow(['Companies Visited', request.companies_visited])
    writer.writerow(['Total Time', f'{request.total_time:.1f} minutes'])
    writer.writerow(['Total Score', f'{request.total_score:.1f}'])
    writer.writerow([])

    # Write route
    writer.writerow(['Route Details'])
    writer.writerow([
        'Stop #',
        'Company ID',
        'Booth Number',
        'Arrival Time (min)',
        'Travel Time (min)',
        'Service Time (min)',
        'Score'
    ])

    for i, stop in enumerate(request.route, 1):
        writer.writerow([
            i,
            stop.get('company_id', ''),
            stop['booth_number'],
            f"{stop['arrival_time']:.1f}",
            f"{stop['travel_time']:.1f}",
            f"{stop['service_time']:.1f}",
            f"{stop['score']:.1f}"
        ])

    # Get CSV content
    csv_content = output.getvalue()

    # Return as downloadable file
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=itinerary_{request.user_name.replace(' ', '_')}.csv"
        }
    )


@router.post("/talking-points-pdf")
async def export_talking_points_pdf(
    company_name: str,
    talking_points: List[str],
    questions: List[str],
    conversation_starters: List[str],
    user_name: str
):
    """
    Export talking points as PDF.

    Args:
        company_name: Company name
        talking_points: List of talking points
        questions: List of questions
        conversation_starters: List of conversation starters
        user_name: User's name

    Returns:
        PDF file download
    """
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="PDF generation not available"
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph(f"Talking Points: {company_name}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))

    # Conversation Starters
    elements.append(Paragraph("Conversation Starters", styles['Heading2']))
    elements.append(Spacer(1, 0.1 * inch))
    for starter in conversation_starters:
        elements.append(Paragraph(f"• {starter}", styles['Normal']))
        elements.append(Spacer(1, 0.1 * inch))

    elements.append(Spacer(1, 0.2 * inch))

    # Talking Points
    elements.append(Paragraph("Key Points to Mention", styles['Heading2']))
    elements.append(Spacer(1, 0.1 * inch))
    for point in talking_points:
        elements.append(Paragraph(f"• {point}", styles['Normal']))
        elements.append(Spacer(1, 0.1 * inch))

    elements.append(Spacer(1, 0.2 * inch))

    # Questions
    elements.append(Paragraph("Questions to Ask", styles['Heading2']))
    elements.append(Spacer(1, 0.1 * inch))
    for question in questions:
        elements.append(Paragraph(f"• {question}", styles['Normal']))
        elements.append(Spacer(1, 0.1 * inch))

    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=talking_points_{company_name.replace(' ', '_')}.pdf"
        }
    )
