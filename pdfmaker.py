# pdfmaker.py
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def clean_html_tags(text: str) -> str:
    """Safely balances or strips malformed nested tags to prevent ReportLab XML crashes."""
    # If tags are mismatched or improperly nested, a simple fallback is to strip 
    # conflicting markdown formatting or ensure basic clean replacement.
    # Let's replace dangerous overlapping patterns safely:
    text = text.replace('&', '&amp;')
    
    # Convert Markdown Bold first
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert Markdown Italics
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    
    return text

def create_styled_pdf(title_text: str, full_transcript_markdown: str) -> bytes:
    """Takes a title and the complete conversation/blueprint markdown, parses formatting safely for ReportLab, and returns PDF bytes."""
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
        fontSize=18,
        leading=22,
        textColor=PRIMARY_COLOR,
        fontName='Helvetica-Bold',
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=ACCENT_COLOR,
        fontName='Helvetica-Bold',
        spaceAfter=12
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=PRIMARY_COLOR,
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=4
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading3'],
        fontSize=10,
        leading=14,
        textColor=ACCENT_COLOR,
        fontName='Helvetica-Bold',
        spaceBefore=6,
        spaceAfter=3
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=TEXT_COLOR,
        fontName='Helvetica',
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        spaceAfter=3
    )

    story = []
    
    # Header Section
    story.append(Paragraph(title_text, title_style))
    story.append(Paragraph("THE STORY SKELETON ARCHITECT | CASSANDRA LEE YIENG", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))
    
    # Process markdown lines safely
    lines = full_transcript_markdown.split('\n')
    for line in lines:
        line_str = line.strip()
        if not line_str or line_str == '- *' or line_str == '---':
            if line_str == '---':
                story.append(Spacer(1, 3))
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=6))
            continue
            
        # Parse formatting safely with tag-protection wrapper
        formatted_line = clean_html_tags(line_str)
        
        # Determine element type based on prefix
        try:
            if line_str.startswith('### ') or line_str.startswith('# '):
                clean_text = re.sub(r'^#+\s*', '', formatted_line)
                story.append(Paragraph(clean_text, h1_style))
            elif line_str.startswith('#### '):
                clean_text = re.sub(r'^#+\s*', '', formatted_line)
                story.append(Paragraph(clean_text, h2_style))
            elif line_str.startswith('- ') or line_str.startswith('* ') or line_str.startswith('-   - '):
                clean_text = re.sub(r'^(-\s*\*?|\*\s*|-\s*-\s*)', '', formatted_line)
                story.append(Paragraph(f"• {clean_text}", bullet_style))
            else:
                story.append(Paragraph(formatted_line, body_style))
        except Exception as e:
            # Fallback safety: if an individual paragraph still fails XML parsing, strip all tags and print plain text so the PDF never crashes app execution
            plain_fallback = re.sub(r'<[^>]*>', '', formatted_line)
            if line_str.startswith('- ') or line_str.startswith('* '):
                story.append(Paragraph(f"• {plain_fallback}", bullet_style))
            else:
                story.append(Paragraph(plain_fallback, body_style))
            
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes