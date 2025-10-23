# --- START OF FILE app/utils.py ---

import arabic_reshaper
from bidi.algorithm import get_display
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

def calculate_age_group(age):
    """Categorizes an age into a predefined group."""
    if age <= 18:
        return '0-18'
    elif 19 <= age <= 35:
        return '19-35'
    elif 36 <= age <= 50:
        return '36-50'
    elif 51 <= age <= 65:
        return '51-65'
    else:
        return '65+'

def _arabic_text(text):
    """Reshapes and reverses Arabic text for correct rendering in ReportLab."""
    if not text:
        return ''
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

def generate_beneficiary_pdf(record):
    """
    Generates a professional-looking PDF for a beneficiary record.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

    # Register a font that supports Arabic characters.
    font_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/System/Library/Fonts/Supplemental/DejaVuSans.ttf',
        'C:/Windows/Fonts/DejaVuSans.ttf',
        'DejaVuSans.ttf'
    ]
    font_name = 'DejaVuSans'
    try:
        for font_path in font_paths:
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                break
            except:
                continue
        else:
            font_name = 'Helvetica'
    except Exception:
        font_name = 'Helvetica'

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ArabicTitle', fontName=font_name, fontSize=18, alignment=2, spaceAfter=20))
    styles.add(ParagraphStyle(name='ArabicHeader', fontName=font_name, fontSize=12, alignment=2, spaceAfter=10))
    styles.add(ParagraphStyle(name='ArabicBodyText', fontName=font_name, fontSize=10, alignment=2)) # Right-aligned for labels
    styles.add(ParagraphStyle(name='ArabicBodyTextValue', fontName=font_name, fontSize=10, alignment=0)) # Left-aligned for values

    elements = []

    # --- Title ---
    elements.append(Paragraph(_arabic_text("تقرير المستفيد"), styles['ArabicTitle']))

    # --- Beneficiary Details Table ---
    elements.append(Paragraph(_arabic_text("البيانات الشخصية"), styles['ArabicHeader']))

    data = [
        [_arabic_text(record.full_name), _arabic_text("الاسم الكامل")],
        [_arabic_text(record.id_passport_number), _arabic_text("رقم الهوية/جواز السفر")],
        [record.date_of_birth.strftime('%Y-%m-%d'), _arabic_text("تاريخ الميلاد")],
        [_arabic_text(record.gender), _arabic_text("الجنس")],
        [_arabic_text(record.marital_status), _arabic_text("الحالة الاجتماعية")],
        [_arabic_text(record.phone_number or '-'), _arabic_text("رقم الهاتف")],
        [_arabic_text(record.address or '-'), _arabic_text("العنوان")],
        [_arabic_text(record.status), _arabic_text("الحالة")],
        [record.created_at.strftime('%Y-%m-%d %H:%M'), _arabic_text("تاريخ الإنشاء")]
    ]

    table = Table(data, colWidths=[3.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'DejaVuSans', 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),   # Values
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Labels
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.25*inch))

    # --- Family Members Table (if applicable) ---
    if record.head_of_household_id is None: # It's a head of household
        family_members = record.family_members.all()
        if family_members:
            elements.append(Paragraph(_arabic_text("أفراد الأسرة"), styles['ArabicHeader']))
            family_data = [[_arabic_text('الحالة'), _arabic_text('العمر'), _arabic_text('رقم الهوية'), _arabic_text('الاسم الكامل')]]
            for member in family_members:
                family_data.append([
                    _arabic_text(member.status),
                    str(member.age),
                    _arabic_text(member.id_passport_number),
                    _arabic_text(member.full_name)
                ])

            family_table = Table(family_data)
            family_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'DejaVuSans', 10),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(family_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
