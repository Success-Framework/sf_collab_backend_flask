import os
import shutil
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# -----------------------------------------
# CONFIG — EDIT THESE PATHS
# -----------------------------------------
SOURCE_DIR = "app/models"          # folder with your code
OUTPUT_PDF = "all_models_structured.pdf"          # output PDF file
# -----------------------------------------

def create_structured_pdf(src_dir, pdf_path):
    """Reads all files from a directory and writes them to a PDF in IDE format."""
    styles = getSampleStyleSheet()
    body = []

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        title="Project Code (Structured Format)"
    )

    file_number = 1

    # Walk through all files
    for root, _, files in os.walk(src_dir):
        for file in sorted(files):
            file_path = os.path.join(root, file)

            # Try reading file
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
            except Exception as e:
                code = f"<< ERROR READING FILE: {e} >>"

            # Header
            header = f"{file_number} — {file}"
            body.append(Paragraph(f"<b>{header}</b>", styles["Heading4"]))
            body.append(Spacer(1, 0.15 * inch))

            # Preformatted code block (preserves indentation exactly!)
            body.append(Preformatted(code, styles["Code"]))
            body.append(Spacer(1, 0.25 * inch))
            body.append(Paragraph("<hr/>", styles["BodyText"]))
            body.append(Spacer(1, 0.20 * inch))

            file_number += 1

    # Build the PDF
    doc.build(body)
    print(f"[✓] PDF created: {pdf_path}")


# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    create_structured_pdf(SOURCE_DIR, OUTPUT_PDF)
