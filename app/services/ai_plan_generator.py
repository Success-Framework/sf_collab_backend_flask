from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from datetime import datetime
import os

def generate_plan_section(plan, sections, financials, projections, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    story = []

    # Cover Page
    story.append(Paragraph(plan.title, styles['Title']))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"<b>Industry:</b> {plan.industry}", styles['Normal']))
    story.append(Paragraph(f"<b>Stage:</b> {plan.stage}", styles['Normal']))
    story.append(Paragraph(
        f"<b>Generated on:</b> {datetime.utcnow().strftime('%Y-%m-%d')}",
        styles['Normal']
    ))
    story.append(Spacer(1, 1 * inch))

    # Table of Contents
    story.append(Paragraph("Table of Contents", styles['Heading1']))
    toc_items = [
        "Executive Summary",
        "Problem & Solution",
        "Market Overview",
        "Business Model",
        "Operations Plan",
        "Marketing Strategy",
        "Financial Overview"
    ]
    for item in toc_items:
        story.append(Paragraph(item, styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))

    # Sections
    for section in sections:
        story.append(Paragraph(section.type.replace("_", " ").title(), styles['Heading1']))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(section.content, styles['Normal']))
        story.append(Spacer(1, 0.4 * inch))

    # Financial Table
    if projections:
        story.append(Paragraph("Financial Summary", styles['Heading1']))

        table_data = [["Year", "Revenue", "Expenses", "Profit/Loss"]]
        for p in projections:
            table_data.append([
                p["year"],
                f"${p['revenue']}",
                f"${p['expenses']}",
                f"${p['profit']}"
            ])

        story.append(Table(table_data, hAlign='LEFT'))

    doc.build(story)
