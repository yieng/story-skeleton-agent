# pdfmaker.py
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_styled_pdf(title_text: str, content_markdown: str) -> bytes:
    """Takes a title and markdown content, parses formatting, and returns PDF bytes in memory."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    PRIMARY_COLOR = colors.HexColor('#1E293B')   # Slate Dark
    ACCENT_COLOR = colors.HexColor('#2563EB')    # Blue Accent
    TEXT_COLOR = colors.HexColor('#334155')      # Muted Slate Body
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR,
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=ACCENT_COLOR,
        fontName='Helvetica-Bold',
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=PRIMARY_COLOR,
        fontName='Helvetica-Bold',
        spaceBefore=14,
        spaceAfter=6
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading3'],
        fontSize=12,
        leading=16,
        textColor=ACCENT_COLOR,
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontSize=10,
        leading=15,
        textColor=TEXT_COLOR,
        fontName='Helvetica',
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        spaceAfter=4
    )

    story = []
    
    # Header Section
    story.append(Paragraph(title_text, title_style))
    story.append(Paragraph("THE STORY SKELETON ARCHITECT | CASSANDRA LEE", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))
    
    # Simple Markdown Parser
    lines = content_markdown.split('\n')
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line_str)
        formatted_line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted_line)
        
        if line_str.startswith('### '):
            clean_text = formatted_line.replace('### ', '')
            story.append(Paragraph(clean_text, h1_style))
        elif line_str.startswith('#### '):
            clean_text = formatted_line.replace('#### ', '')
            story.append(Paragraph(clean_text, h2_style))
        elif line_str.startswith('- ') or line_str.startswith('* '):
            clean_text = formatted_line[2:]
            story.append(Paragraph(f"• {clean_text}", bullet_style))
        elif line_str.startswith('---'):
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=10))
        else:
            story.append(Paragraph(formatted_line, body_style))
            
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes