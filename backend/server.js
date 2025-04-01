const express = require('express');
const cors = require('cors');
const fs = require('fs');
const app = express();
const port = 5000;

app.use(cors());
app.use(express.json()); // Pour analyser le corps JSON des requêtes

// Lire les évaluations depuis le fichier JSON
app.get('/evaluations', (req, res) => {
  fs.readFile('data.json', (err, data) => {
    if (err) {
      return res.status(500).send('Erreur de lecture du fichier');
    }
    res.json(JSON.parse(data));
  });
});

// Sauvegarder une nouvelle évaluation
app.post('/evaluations', (req, res) => {
  const { text } = req.body;

  if (!text) {
    return res.status(400).send('Le texte est requis');
  }

  fs.readFile('data.json', (err, data) => {
    if (err) {
      return res.status(500).send('Erreur de lecture du fichier');
    }

    const evaluations = JSON.parse(data);
    evaluations.push({ text });

    fs.writeFile('data.json', JSON.stringify(evaluations, null, 2), (err) => {
      if (err) {
        return res.status(500).send('Erreur lors de l\'écriture dans le fichier');
      }
      res.status(201).send('Texte sauvegardé');
    });
  });
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
