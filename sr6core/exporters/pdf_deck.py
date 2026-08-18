"""
ReportLab PDF Reference Card Deck Exporter for SR6.
Generates printable physical/digital index cards and postcards (1 card per page).
"""

import os
import io
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

# Page Size Dimensions in points (1 inch = 72 points)
CARD_PAGE_SIZES = {
    "postcard_4x5.5": (4.25 * inch, 5.5 * inch),
    "index_4x6": (4.0 * inch, 6.0 * inch),
    "index_3x5": (3.0 * inch, 5.0 * inch),
    "letter_grid": (8.5 * inch, 11.0 * inch),
}

# Theme Colors
C_PRIMARY = colors.HexColor("#0f172a")     # Dark Slate
C_SECONDARY = colors.HexColor("#0369a1")   # Deep Sky Blue
C_ACCENT = colors.HexColor("#0284c7")      # Cyan Blue
C_BG_LIGHT = colors.HexColor("#f8fafc")    # Light Slate
C_TEXT_DARK = colors.HexColor("#0f172a")
C_TEXT_MUTED = colors.HexColor("#475569")
C_BORDER = colors.HexColor("#94a3b8")


def generate_pdf_card_deck(
    cards: List[Dict[str, Any]],
    output_path: str,
    card_size: str = "postcard_4x5.5",
    char_name: str = "Shadowrunner"
) -> str:
    """
    Generates a multi-page PDF where each page is an individual reference/stat card.
    """
    page_width, page_height = CARD_PAGE_SIZES.get(card_size, CARD_PAGE_SIZES["postcard_4x5.5"])
    margin = 0.25 * inch

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(page_width, page_height),
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )

    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.white
    )
    
    cat_style = ParagraphStyle(
        'CardCat',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=2, # Right
        textColor=colors.HexColor("#e0f2fe")
    )
    
    stat_label_style = ParagraphStyle(
        'StatLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=C_TEXT_DARK
    )
    
    stat_val_style = ParagraphStyle(
        'StatVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9,
        textColor=C_TEXT_DARK
    )
    
    body_style = ParagraphStyle(
        'CardBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=C_TEXT_DARK
    )
    
    footer_style = ParagraphStyle(
        'CardFooter',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7,
        leading=9,
        textColor=C_TEXT_MUTED
    )

    story = []
    usable_width = page_width - (2 * margin)
    usable_height = page_height - (2 * margin)

    for idx, card in enumerate(cards):
        card_elements = []
        name = card.get("name", "Card").upper()
        cat = card.get("category", "REFERENCE").upper()

        # 1. Card Header Bar
        header_table = Table(
            [[Paragraph(name, title_style), Paragraph(cat, cat_style)]],
            colWidths=[usable_width * 0.68, usable_width * 0.32]
        )
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), C_SECONDARY),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        card_elements.append(header_table)
        card_elements.append(Spacer(1, 4))

        # 2. Stats Grid / Table
        stats = card.get("stats", {})
        if stats:
            stat_cells = []
            stat_items = list(stats.items())
            # Format in 2 columns
            for i in range(0, len(stat_items), 2):
                row = []
                k1, v1 = stat_items[i]
                row.append(Paragraph(f"<b>{k1.replace('_', ' ').title()}:</b> {v1}", stat_val_style))
                if i + 1 < len(stat_items):
                    k2, v2 = stat_items[i+1]
                    row.append(Paragraph(f"<b>{k2.replace('_', ' ').title()}:</b> {v2}", stat_val_style))
                else:
                    row.append(Paragraph("", stat_val_style))
                stat_cells.append(row)

            stat_table = Table(stat_cells, colWidths=[usable_width * 0.5, usable_width * 0.5])
            stat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), C_BG_LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            card_elements.append(stat_table)
            card_elements.append(Spacer(1, 4))

        # 3. Modifications / Notes Badge
        mods = card.get("modifications", [])
        if mods:
            mods_text = "<b>Modifications:</b> " + ", ".join(str(m) for m in mods)
            mods_table = Table([[Paragraph(mods_text, stat_val_style)]], colWidths=[usable_width])
            mods_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#bfdbfe")),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ]))
            card_elements.append(mods_table)
            card_elements.append(Spacer(1, 4))

        # 4. Verbatim Body / Rules Text
        vault_text = card.get("vault_text", "")
        if vault_text:
            import re
            cleaned = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", vault_text)
            cleaned = re.sub(r"\*\*==>.*?<==\*\*", "", cleaned)
            cleaned = re.sub(r"\*\*-----.*?-----\*\*", "", cleaned)
            cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.IGNORECASE)
            # Escape XML entities while preserving <b> tags
            cleaned = cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            cleaned = cleaned.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
            cleaned = cleaned.strip()
            # Collapse excessive breaks
            cleaned = re.sub(r"(\r?\n){3,}", "\n\n", cleaned)
            cleaned = cleaned.replace("\n", "<br/>")
            card_elements.append(Paragraph(cleaned, body_style))
            card_elements.append(Spacer(1, 4))

        # 5. Card Footer (Citation + ID)
        citation = card.get("citation", "")
        card_id = card.get("id", "")
        footer_text = f"{char_name} | {card_id}" + (f" | {citation}" if citation else "")
        footer_table = Table(
            [[Paragraph(footer_text, footer_style)]],
            colWidths=[usable_width]
        )
        footer_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 0.5, C_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        card_elements.append(footer_table)

        # Wrap in full page container
        story.append(KeepTogether(card_elements))
        if idx < len(cards) - 1:
            story.append(PageBreak())

    doc.build(story)
    return output_path


def generate_pdf_base_sheet(char_data: Dict[str, Any], output_path: str) -> str:
    """
    Generates a clean, printable 1-2 page Base Character Sheet PDF on Letter/A4 format.
    """
    page_width, page_height = 8.5 * inch, 11.0 * inch
    margin = 0.5 * inch

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(page_width, page_height),
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )

    styles = getSampleStyleSheet()
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        textColor=colors.white
    )
    section_style = ParagraphStyle(
        'DocSection',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=C_SECONDARY
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10.5,
        textColor=C_TEXT_DARK
    )
    cell_regular = ParagraphStyle(
        'CellRegular',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=10.5,
        textColor=C_TEXT_DARK
    )

    identity = char_data.get("identity", {})
    attrs = char_data.get("attributes", {})
    skills = char_data.get("skills", [])
    handle = identity.get("handle", "Unknown").upper()

    usable_width = page_width - (2 * margin)
    story = []

    # Title Header
    header_tbl = Table(
        [[Paragraph(f"SHADOWRUN 6E - CHARACTER DOSSIER: {handle}", h1_style)]],
        colWidths=[usable_width]
    )
    header_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 8))

    # Identity Grid
    meta = identity.get("metatype", "Human")
    stream = identity.get("stream", "N/A")
    rname = identity.get("real_name", "N/A")
    id_rows = [
        [Paragraph("<b>Handle:</b> " + handle, cell_regular), Paragraph("<b>Metatype:</b> " + meta, cell_regular)],
        [Paragraph("<b>Real Name:</b> " + rname, cell_regular), Paragraph("<b>Stream / Archetype:</b> " + stream, cell_regular)],
    ]
    id_tbl = Table(id_rows, colWidths=[usable_width * 0.5, usable_width * 0.5])
    id_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(id_tbl)
    story.append(Spacer(1, 8))

    # Attributes Grid
    story.append(Paragraph("ATTRIBUTES & DERIVATIONS", section_style))
    story.append(Spacer(1, 4))
    
    attr_cols = [usable_width / 10] * 10
    attr_headers = ["BOD", "AGI", "REA", "STR", "WIL", "LOG", "INT", "CHA", "EDG", "RES"]
    attr_vals = [str(attrs.get(k.lower(), 1)) for k in ["body", "agility", "reaction", "strength", "willpower", "logic", "intuition", "charisma", "edge", "resonance"]]
    
    attr_tbl = Table(
        [[Paragraph(f"<b>{h}</b>", cell_bold) for h in attr_headers],
         [Paragraph(v, cell_regular) for v in attr_vals]],
        colWidths=attr_cols
    )
    attr_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(attr_tbl)
    story.append(Spacer(1, 8))

    # Skills Table
    story.append(Paragraph("ACTIVE SKILLS & DICE POOLS", section_style))
    story.append(Spacer(1, 4))
    skill_rows = [[
        Paragraph("<b>Skill</b>", cell_bold),
        Paragraph("<b>Attr</b>", cell_bold),
        Paragraph("<b>Rating</b>", cell_bold),
        Paragraph("<b>Specialization</b>", cell_bold),
        Paragraph("<b>Total Pool</b>", cell_bold)
    ]]
    for s in skills:
        s_attr = s.get("attribute", "logic").lower()
        s_rating = int(s.get("rating", 1))
        attr_val = int(attrs.get(s_attr, 1))
        pool = attr_val + s_rating
        spec = s.get("specialization", "-")
        skill_rows.append([
            Paragraph(s.get("name", "Skill"), cell_regular),
            Paragraph(s_attr.upper(), cell_regular),
            Paragraph(str(s_rating), cell_regular),
            Paragraph(str(spec), cell_regular),
            Paragraph(f"<b>{pool}d6</b>" + (f" (+2 {spec})" if spec != "-" else ""), cell_regular)
        ])
    skill_tbl = Table(skill_rows, colWidths=[usable_width * 0.28, usable_width * 0.12, usable_width * 0.12, usable_width * 0.28, usable_width * 0.20])
    skill_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(skill_tbl)
    story.append(Spacer(1, 8))

    doc.build(story)
    return output_path

