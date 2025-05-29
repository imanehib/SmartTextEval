import os
import sys

print(f"Chemin actuel : {os.getcwd()}")
print(f"sys.path : {sys.path}")


try:
    import myproject.text_analysis
    print("Importation réussie!")
except ImportError as e:
    print("Erreur d'importation:", e)
