from pydantic import BaseModel
from typing import List

class DecodedData(BaseModel):
    final_text: str         # réponse finale de l'étudiant
    context: str            # sujet de l'exercice
    text_type: str          # type de texte dans l'exercice (argumentatif, narratif...)
    time_list: List[int]    # liste des timestamps à chaque frappe clavier (ms)
    text_list: List[str]    # liste contenant l'état du texte complet à chaque frappe clavier
    cursor_list: List[str]  # liste des positions du curseur à chaque frappe clavier
    student_id: str         # identifiant de l'étudiant
    exercise_id: str        # identifiant de l'exercice
    
    class Config:
        str_strip_whitespace = True
        validate_by_name = True
