const express = require("express");
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const app = express();
app.use(cors());

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, '/index.html'));
    console.log("Index")
});

app.get("/bumList.json", (req, res) => {
    res.sendFile(path.join(__dirname, '../lib/bumList.json'));
    console.log("Bum List")
});

app.get("/teamList.json", (req, res) => {
    res.sendFile(path.join(__dirname, '../lib/teamList.json'));
    console.log("Team List")
});

app.listen(3000, () => {
    console.log("Listen on the port 3000...");
});