import keyboard
import sqlite3

# Initialisation des listes
cursor_positions = []
paragraph_progression = []

# Connexion à la base SQLite
conn = sqlite3.connect("typing_data.db")
cursor = conn.cursor()

# Création de la table si elle n'existe pas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS typing_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cursor_position INTEGER,
        paragraph_text TEXT
    )
""")
conn.commit()

# Texte en cours de frappe
current_text = ""

def on_key_event(event):
    global current_text

    # Vérifie si c'est une vraie touche (évite Shift, Ctrl, etc.)
    if len(event.name) == 1 or event.name in ["space", "backspace"]:
        
        # Gestion de la touche retour arrière
        if event.name == "backspace":
            current_text = current_text[:-1]
        elif event.name == "space":
            current_text += " "  # Ajout d'un espace
        else:
            current_text += event.name  # Ajout de la lettre tapée
        
        # Position actuelle du curseur
        cursor_position = len(current_text)

        # Mise à jour des listes
        cursor_positions.append(cursor_position)
        paragraph_progression.append(current_text)

        # Sauvegarde en base de données
        cursor.execute("INSERT INTO typing_data (cursor_position, paragraph_text) VALUES (?, ?)", 
                       (cursor_position, current_text))
        conn.commit()

        # Affichage en temps réel
        print(f"\nCursor Positions: {cursor_positions}")
        print(f"Paragraph Progression: {paragraph_progression}")

# Écoute le clavier en temps réel
keyboard.on_press(on_key_event)

print("🔴 Enregistrement des frappes... (Appuie sur 'Échap' pour quitter)")
keyboard.wait("esc")

# Fermeture propre de la base
conn.close()
