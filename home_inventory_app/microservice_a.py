import zmq
import pandas as pd
import json
import io

def json_to_csv(json_data):

    if isinstance(json_data, dict):
        json_data = [json_data]

    data_frame = pd.json_normalize(json_data)
    data_frame.fillna("N/A", inplace=True)

    csv_output = io.StringIO()
    data_frame.to_csv(csv_output, index=False)
    return csv_output.getvalue()

print("Microservice running...")

#ZeroMQ context and socket for communication
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #Waiting for incoming message
    inc_message = socket.recv_json()
    print("Received data from Node.js:", inc_message)

    #converting the JSON file to CSV
    csv_data = json_to_csv(inc_message)
    print("CSV data generated:", csv_data[:100])

    #Sending back CSV data file
    socket.send_string(csv_data)
