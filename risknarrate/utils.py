# utils.py
from io import BytesIO
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def export_pdf_bytes(text: str, title: str = "RiskNarrate Report") -> bytes:
    """
    Create a Unicode-safe PDF in memory and return its bytes.
    Designed for Streamlit st.download_button().
    """

    buffer = BytesIO()

    # --- Font setup (Unicode-safe) ---
    # Put a Unicode font file in your project (recommended).
    # Example path: assets/DejaVuSans.ttf
    font_path = os.path.join("assets", "DejaVuSans.ttf")

    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
        font_name = "DejaVuSans"
    else:
        # Works but may not render all Unicode chars perfectly
        font_name = "Helvetica"

    # --- Build PDF ---
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
        title=title,
    )

    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    body.fontName = font_name
    body.fontSize = 10
    body.leading = 14

    h = styles["Heading2"]
    h.fontName = font_name

    story = []
    story.append(Paragraph(title, h))
    story.append(Spacer(1, 12))

    # ReportLab Paragraph supports a small HTML-like subset.
    # Escape special chars and convert newlines to <br/>
    safe = (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
    )

    story.append(Paragraph(safe, body))
    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes