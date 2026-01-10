import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
EXPORT_DIR = os.path.join(BASE_DIR, 'uploads', 'business_plans')
os.makedirs(EXPORT_DIR, exist_ok=True)


def export_business_plan_pdf(plan, sections, financials):
    filename = f"business_plan_{plan.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    story = []

    # ---------------- COVER PAGE ----------------
    story.append(Paragraph(plan.title, styles['Title']))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"<b>Industry:</b> {plan.industry}", styles['Normal']))
    story.append(Paragraph(f"<b>Stage:</b> {plan.stage}", styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(
        f"Generated on {datetime.utcnow().strftime('%Y-%m-%d')}",
        styles['Italic']
    ))
    story.append(PageBreak())

    # ---------------- SECTIONS ----------------
    ordered_sections = sorted(sections, key=lambda s: s.type)

    for section in ordered_sections:
        title = section.type.replace("_", " ").title()
        story.append(Paragraph(title, styles['Heading1']))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(section.content.replace("\n", "<br/>"), styles['Normal']))
        story.append(Spacer(1, 0.4 * inch))

    # ---------------- FINANCIALS ----------------
    if financials:
        story.append(PageBreak())
        story.append(Paragraph("Financial Overview", styles['Heading1']))
        story.append(Spacer(1, 0.3 * inch))

        projections = financials.assumptions.get("projection_years", 3)

        story.append(Paragraph(
            f"Revenue and cost projections over {projections} years.",
            styles['Normal']
        ))

    doc.build(story)
    return file_path

