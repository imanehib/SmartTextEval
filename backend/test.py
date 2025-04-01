from transformers import pipeline

# Charger un modèle pré-entraîné pour l'analyse de sentiment avec TensorFlow
nlp = pipeline("sentiment-analysis", framework="tf")

# Exemple de texte à analyser
result = nlp("I love programming!")
print(result)
