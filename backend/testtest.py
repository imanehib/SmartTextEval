import os
import sys

print(f"Chemin actuel : {os.getcwd()}")
print(f"sys.path : {sys.path}")

# Essaie d'importer directement text_analysis
try:
    import myproject.text_analysis
    print("Importation réussie!")
except ImportError as e:
    print("Erreur d'importation:", e)
