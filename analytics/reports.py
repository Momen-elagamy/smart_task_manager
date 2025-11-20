import csv
from io import StringIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def export_csv(data):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(data[0].keys())
    for item in data:
        writer.writerow(item.values())
    buffer.seek(0)
    return buffer.getvalue()

def export_pdf(data):
    buffer = StringIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []
    for item in data:
        text = f"{item['project_name']}: {item['completion_rate']}% completed"
        elements.append(Paragraph(text, styles["Normal"]))
        elements.append(Spacer(1, 12))
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
