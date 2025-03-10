# Benjamin Fleming
# OSU - CS 361
# 03/09/2025

import zmq
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def json_to_pdf(json_data):
    # ensure json_data is a list of dictionaries
    if isinstance(json_data, dict):
        json_data = [json_data]

    # define the order of columns and their header labels
    columns = ["category", "subcategory", "item", "purchase_date", "value", "image"]
    header = ["Category", "SubCategory", "Item", "Purchase Date", "Value", "Image"]

    # build table data with header row first
    data = [header]
    for item in json_data:
        row = [str(item.get(col, "N/A")) for col in columns]
        data.append(row)

    # create a bytes buffer for the PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # add a title to the PDF
    elements.append(Paragraph("Home Inventory Export", styles['Title']))
    elements.append(Spacer(1, 12))

    # create the table with data and apply style
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.gray),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(style)

    elements.append(table)
    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

print("PDF Export Microservice running on port 5556......")

# setup ZeroMQ context and socket for communication
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")  # Using a different port from the CSV microservice

while True:
    # wait for incoming message containing JSON data
    inc_message = socket.recv_json()
    print("Received data for PDF export from Node.js:", inc_message)

    # convert JSON data to PDF
    pdf_data = json_to_pdf(inc_message)
    print("PDF generated, size: {} bytes".format(len(pdf_data)))

    # send the PDF binary data back over ZeroMQ
    socket.send(pdf_data)