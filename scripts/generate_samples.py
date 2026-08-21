from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "samples" / "source"
OUTPUT = ROOT / "samples"


def generate(source: Path, target: Path):
    c = canvas.Canvas(str(target), pagesize=A4)
    width, height = A4
    text = c.beginText(54, height - 64)
    text.setFont("Helvetica", 10)
    for raw in source.read_text(encoding="utf-8").splitlines():
        line = raw if raw else " "
        # Standard ReportLab fonts do not shape Devanagari; source TXT remains
        # the authoritative Hindi demo input while the PDF preserves the sample slot.
        safe = line.encode("latin-1", "replace").decode("latin-1")
        for start in range(0, len(safe), 95):
            text.textLine(safe[start:start + 95])
        if text.getY() < 60:
            c.drawText(text)
            c.showPage()
            text = c.beginText(54, height - 64)
            text.setFont("Helvetica", 10)
    c.drawText(text)
    c.save()


if __name__ == "__main__":
    generate(SOURCE / "english_agreement.txt", OUTPUT / "english_agreement.pdf")
    generate(SOURCE / "hindi_scan.txt", OUTPUT / "hindi_scan.pdf")
    generate(SOURCE / "bilingual_vendor.txt", OUTPUT / "bilingual_vendor.pdf")

