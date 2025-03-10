# Benjamin Fleming
# OSU - CS 361
# 03/09/2025
import zmq
import smtplib
from email.message import EmailMessage

def send_inventory_email(inventory, recipient_email):
    # Configure your SMTP server settings (example uses Gmail)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'benjamin.e.fleming@gmail.com'
    sender_password = 'gzon lrej zckm wmsy'

    # Build the email body from the inventory data
    body = "Your Home Inventory:\n\n"
    for item in inventory:
        body += f"Category: {item.get('category', 'N/A')}\n"
        body += f"SubCategory: {item.get('subcategory', 'N/A')}\n"
        body += f"Item: {item.get('item', 'N/A')}\n"
        body += f"Purchase Date: {item.get('purchase_date', 'N/A')}\n"
        body += f"Value: {item.get('value', 'N/A')}\n"
        body += f"Image: {item.get('image', 'N/A')}\n"
        body += "-------------------------\n"

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = 'Your Home Inventory'
    msg['From'] = 'your-email@example.com'
    msg['To'] = recipient_email



    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return "Email sent successfully"
    except Exception as e:
        return f"Failed to send email: {e}"

print("Email Inventory Microservice running on port 5557...")

# Setup ZeroMQ REP socket on a new port (5557)
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")

while True:
    # Expecting a JSON with two keys: 'email' and 'inventory'
    message = socket.recv_json()
    print("Received data for email microservice:", message)
    recipient_email = message.get("email")
    inventory = message.get("inventory", [])
    result = send_inventory_email(inventory, recipient_email)
    socket.send_string(result)