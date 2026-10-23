"""Create a PDF copy of the rendered slide deck, preserving a searchable text layer."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
PPTX = ROOT / "reports/Relatorio_Capstone.pptx"
PDF = ROOT / "reports/Relatorio_Capstone.pdf"
PREVIEWS = ROOT / ".build/presentation/previews"
EMU_PER_INCH = 914400
PAGE_W, PAGE_H = 1280.0, 720.0
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def extract_slide_text(archive: ZipFile, slide_num: int) -> str:
    name = f"ppt/slides/slide{slide_num}.xml"
    root = ET.fromstring(archive.read(name))
    # Preserve text in its slide order, including table cell content and notes labels.
    paragraphs = []
    for paragraph in root.findall(".//a:p", NS):
        value = "".join(node.text or "" for node in paragraph.findall(".//a:t", NS)).strip()
        if value:
            paragraphs.append(value)
    return "\n".join(paragraphs)


def main() -> None:
    slides = sorted(PREVIEWS.glob("slide-*.png"))
    if not slides:
        raise FileNotFoundError(f"No rendered slide images in {PREVIEWS}")
    with ZipFile(PPTX) as archive:
        texts = [extract_slide_text(archive, i) for i in range(1, len(slides) + 1)]

    PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = canvas.Canvas(str(PDF), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    doc.setTitle("SpaceX Falcon 9 Landing Success - IBM Applied Data Science Capstone")
    doc.setAuthor("IBM Applied Data Science Capstone")
    doc.setSubject("Final presentation for the SpaceX Falcon 9 landing-success capstone")
    for image, searchable_text in zip(slides, texts):
        doc.drawImage(str(image), 0, 0, width=PAGE_W, height=PAGE_H, preserveAspectRatio=False)
        # Add searchable text in invisible rendering mode, leaving the slide image unchanged.
        obj = doc.beginText(2, 2)
        obj.setFont("Helvetica", 1)
        obj.setTextRenderMode(3)
        for line in searchable_text.splitlines():
            obj.textLine(line)
        doc.drawText(obj)
        doc.showPage()
    doc.save()
    print(f"Created {PDF} with {len(slides)} searchable pages")


if __name__ == "__main__":
    main()
