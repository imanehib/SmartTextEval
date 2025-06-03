const express = require("express");
const cors = require("cors");
const fs = require("fs");

const app = express();
app.use(express.json());
app.use(cors());


app.post("/api/save", (req, res) => {
  const { text } = req.body;
  const data = { text, timestamp: new Date().toISOString() };

  fs.readFile("backend/data.json", "utf8", (err, fileData) => {
    let texts = [];
    if (!err && fileData) {
      texts = JSON.parse(fileData);
    }
    texts.push(data);

    fs.writeFile("backend/data.json", JSON.stringify(texts, null, 2), (err) => {
      if (err) {
        console.error("Erreur lors de l'écriture du fichier", err);
        return res.status(500).json({ message: "Erreur serveur" });
      }
      res.json({ message: "Texte enregistré" });
    });
  });
});

app.listen(5000, () => {
  console.log("Serveur backend sur http://localhost:5000");
});
