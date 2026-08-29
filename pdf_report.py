from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def create_pdf_report(report, filename="business_report.pdf"):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    for line in report.split("\n"):

        story.append(
            Paragraph(line, styles["BodyText"])
        )

    doc.build(story)

    return filename