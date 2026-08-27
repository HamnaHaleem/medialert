import json
import io
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

SRI_LANKA_TZ = ZoneInfo("Asia/Colombo")

def _to_sri_lanka_time(dt: datetime) -> datetime:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(SRI_LANKA_TZ)

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT

INK = HexColor("#16202A")
INK_SOFT = HexColor("#4A5A68")
TEAL = HexColor("#0E6E66")
BORDER = HexColor("#DCDAD2")

RISK_COLORS = {
    "Low": HexColor("#2F7A4F"),
    "Medium": HexColor("#A6690C"),
    "High": HexColor("#B23A34"),
}

FIELD_LABELS = [
    ("age", "Age", "years"), ("sex", "Sex", ""), ("bmi", "BMI", "kg/m2"),
    ("systolic_bp", "Systolic BP", "mmHg"), ("diastolic_bp", "Diastolic BP", "mmHg"),
    ("cholesterol", "Cholesterol", "mg/dL"), ("hdl", "HDL", "mg/dL"), ("ldl", "LDL", "mg/dL"),
    ("glucose", "Glucose", "mg/dL"), ("creatinine", "Creatinine", "mg/dL"),
    ("hemoglobin", "Hemoglobin", "g/dL"), ("wbc", "WBC", "x10^9/L"),
    ("smoking_status", "Smoking status", ""), ("alcohol_use", "Alcohol use", ""),
    ("hypertension", "Hypertension", ""), ("primary_diagnosis", "Primary diagnosis", ""),
    ("medications", "Medications", ""), ("length_of_stay", "Length of stay", "days"),
]

def generate_pdf(record) -> bytes:
    """record: an AssessmentRecord instance (already fetched from the DB)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm, leftMargin=20 * mm, rightMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], textColor=INK, alignment=TA_LEFT, fontSize=20)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], textColor=INK_SOFT, fontSize=10)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], textColor=TEAL, fontSize=11, spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], textColor=INK, fontSize=10, leading=14)
    factor_style = ParagraphStyle("Factor", parent=styles["Normal"], textColor=INK, fontSize=9.5, leading=13, spaceAfter=6)
    disclaimer_style = ParagraphStyle("Disclaimer", parent=styles["Normal"], textColor=INK_SOFT, fontSize=8, leading=11)

    risk_color = RISK_COLORS.get(record.risk_level, INK)
    elements = []

    elements.append(Paragraph("MediAlert", title_style))
    elements.append(Paragraph("30-Day Diabetic Readmission Risk Assessment", subtitle_style))
    elements.append(Spacer(1, 4 * mm))
    elements.append(HRFlowable(width="100%", color=BORDER, thickness=0.75))
    elements.append(Spacer(1, 4 * mm))

    meta_rows = [
        ["Assessment ID:", str(record.id)],
        ["Date:", _to_sri_lanka_time(record.created_at).strftime("%Y-%m-%d %H:%M") + " (Sri Lanka time)" if record.created_at else "-"],
        ["Patient reference:", record.patient_reference or "Not provided"],
    ]
    meta_table = Table(meta_rows, colWidths=[35 * mm, 100 * mm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), INK_SOFT),
        ("TEXTCOLOR", (1, 0), (1, -1), INK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 6 * mm))

    risk_style = ParagraphStyle("Risk", parent=styles["Normal"], textColor=risk_color, fontSize=16, leading=20)
    prob_pct = f"{record.readmission_probability * 100:.1f}%"
    elements.append(Paragraph(f"<b>{record.risk_level} risk</b> &nbsp;&nbsp; ({prob_pct} predicted probability)", risk_style))
    elements.append(Spacer(1, 6 * mm))

    elements.append(Paragraph("Patient Data at Assessment", section_style))
    data_rows = []
    for field, label, unit in FIELD_LABELS:
        value = getattr(record, field, "-")
        if field == "hypertension":
            value = "Yes" if value else "No"
        display = f"{value} {unit}".strip() if unit else str(value)
        data_rows.append([label, display])
        
    half = (len(data_rows) + 1) // 2
    left_rows, right_rows = data_rows[:half], data_rows[half:]
    combined_rows = []
    for i in range(max(len(left_rows), len(right_rows))):
        l = left_rows[i] if i < len(left_rows) else ["", ""]
        r = right_rows[i] if i < len(right_rows) else ["", ""]
        combined_rows.append(l + r)
    data_table = Table(combined_rows, colWidths=[35 * mm, 45 * mm, 35 * mm, 45 * mm])
    data_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), INK_SOFT),
        ("TEXTCOLOR", (2, 0), (2, -1), INK_SOFT),
        ("TEXTCOLOR", (1, 0), (1, -1), INK),
        ("TEXTCOLOR", (3, 0), (3, -1), INK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, BORDER),
    ]))
    elements.append(data_table)
    elements.append(Spacer(1, 4 * mm))

    elements.append(Paragraph("What's Driving This Assessment", section_style))
    try:
        factors = json.loads(record.top_contributing_factors_json)
    except (TypeError, ValueError):
        factors = []
    for f in factors:
        elements.append(Paragraph(f"&bull; {f.get('explanation', '')}", factor_style))

    elements.append(Spacer(1, 8 * mm))
    elements.append(HRFlowable(width="100%", color=BORDER, thickness=0.5))
    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph(
        "This output is a decision-support estimate, not a diagnosis. It is intended to inform "
        "clinical judgment alongside the full patient record, not to replace it. Generated by "
        "MediAlert on " + datetime.now(SRI_LANKA_TZ).strftime("%Y-%m-%d %H:%M") + " (Sri Lanka time).",
        disclaimer_style,
    ))

    doc.build(elements)
    return buffer.getvalue()