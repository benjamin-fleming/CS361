const express = require("express");
const zmq = require("zeromq");
const bodyParser = require("body-parser");
const app = express();
const port = 3000;
const cors = require('cors');


app.use(bodyParser.json());
app.use(cors());

app.post("/convert_json_to_csv", async (req, res) => {
    const data = req.body;
    console.log("Received data from frontend:", data);


    try {
        const socket = new zmq.Request();

        await socket.connect("tcp://localhost:5555");

        console.log("Sending data to microservice...");

        await socket.send(JSON.stringify(data));
        const [csv] = await socket.receive();

        res.setHeader('Content-Disposition', 'attachment; filename=data.csv');

        res.setHeader('Content-Type', 'text/csv');
        res.send(csv.toString());
    } catch (err) {
        console.error("Error receiving response from microservice:", err);
        res.status(500).send("Error processing request.");
    }
});

// Start Server
app.listen(port, () => {
    console.log(`Node.js server listening at http://localhost:${port}`);
});
