import streamlit as st
from transformers import pipeline

# Charger le modèle de détection de langue
classifier = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")

# Interface Streamlit
st.title("Détection de la Langue")

# Zone de texte où l'utilisateur peut entrer un texte
texte = st.text_area("Entrez un texte à analyser :", "")

# Bouton pour lancer l'analyse
if st.button("Valider"):
    if texte:
        # Analyser le texte avec le modèle
        result = classifier(texte)[0]
        st.write(f"Langue détectée : {result['label']}")
        st.write(f"Confiance du modèle : {result['score']:.4f}")
    else:
        st.write("Veuillez entrer un texte.")

# Option de sauvegarde
if st.button("Sauvegarder"):
    if texte:
        with open("texte_sauvegarde.txt", "w") as file:
            file.write(texte)
        st.write("Texte sauvegardé dans 'texte_sauvegarde.txt'")
    else:
        st.write("Aucun texte à sauvegarder.")
