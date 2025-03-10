# Benjamin Fleming
# OSU - CS 361
# 03/09/2025

import zmq
import io
import base64
import matplotlib.pyplot as plt

def generate_analytics(json_data):
    # Aggregate data by category
    totals = {}
    for item in json_data:
        cat = item.get("category", "Unknown")
        try:
            value = float(item.get("value", 0))
        except:
            value = 0.0
        if cat in totals:
            totals[cat]["count"] += 1
            totals[cat]["value"] += value
        else:
            totals[cat] = {"count": 1, "value": value}

    # Prepare data for pie chart based on total value per category
    labels = []
    values = []
    for cat, data in totals.items():
        labels.append(f"{cat} ({data['count']})")
        values.append(data["value"])

    # Create a pie chart
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio for a perfect circle

    # Save the figure to a bytes buffer in PNG format
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    # Encode the image as a base64 string
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Return the analytics information along with the pie chart
    response_data = {
        "analytics": totals,
        "pie_chart": image_base64
    }
    return response_data

print("Analytics Microservice running on port 5558...")

# Set up ZeroMQ context and REP socket on port 5558
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5558")

while True:
    # Wait for incoming JSON data (the inventory list)
    json_data = socket.recv_json()
    print("Received data for analytics microservice:", json_data)
    response_data = generate_analytics(json_data)
    socket.send_json(response_data)