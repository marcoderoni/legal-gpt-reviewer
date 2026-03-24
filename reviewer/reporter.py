# Copyright (c) 2025 Marco De Roni. All rights reserved.
# Licensed under the MIT License — see LICENSE file for details.

import os
from datetime import datetime
from docx import Document
from docx.shared import RGBColor, Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def generate_report(contract_name: str, analysis: str, output_dir: str) -> str:
    """Generates a Word report from GPT analysis output."""

    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.2)
        section.right_margin = Inches(1.2)

    # Title
    title = doc.add_heading("CONTRACT REVIEW REPORT", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = doc.add_paragraph(
        f"Document: {contract_name}\n"
        f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}\n"
        f"Powered by: GPT-4o"
    )
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()

    # Parse and write analysis sections
    lines = analysis.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            doc.add_paragraph()
            continue

        if line.startswith("## "):
            doc.add_heading(line.replace("## ", ""), level=1)
        elif line.startswith("### "):
            doc.add_heading(line.replace("### ", ""), level=2)
        elif line.startswith("- 🔴") or line.startswith("- 🔴"):
            p = doc.add_paragraph(style="List Bullet")
            run = p.add_run(line.replace("- ", ""))
            run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
            run.font.size = Pt(10)
        elif line.startswith("- 🟡"):
            p = doc.add_paragraph(style="List Bullet")
            run = p.add_run(line.replace("- ", ""))
            run.font.color.rgb = RGBColor(0xFF, 0xC0, 0x00)
            run.font.size = Pt(10)
        elif line.startswith("- 🟢"):
            p = doc.add_paragraph(style="List Bullet")
            run = p.add_run(line.replace("- ", ""))
            run.font.color.rgb = RGBColor(0x00, 0x70, 0x00)
            run.font.size = Pt(10)
        elif line.startswith("- "):
            doc.add_paragraph(line, style="List Bullet")
        else:
            p = doc.add_paragraph(line)
            p.runs[0].font.size = Pt(10) if p.runs else None

    os.makedirs(output_dir, exist_ok=True)
    safe_name = contract_name.replace(" ", "_").replace("/", "_")
    path = os.path.join(output_dir, f"gpt_report_{safe_name}.docx")
    doc.save(path)
    return path