import os
import openai
from openai import OpenAI
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextEvaluator:
    def __init__(self, api_key: str):
        """Initialize the TextEvaluator with OpenAI API key."""
        openai.api_key = api_key
        
        # Define evaluation rubrics in French
        self.rubrics = {
            "réponse_consigne": "Évaluez la réponse à la consigne et la prise de position",
            "organisation": "Évaluez l'organisation et la structure du texte",
            "arguments": "Évaluez la qualité des arguments et des exemples",
            "vocabulaire": "Évaluez la richesse et la précision du vocabulaire",
            "grammaire": "Évaluez la correction grammaticale et la syntaxe",
            "orthographe": "Évaluez la maîtrise de l'orthographe",
            "style": "Évaluez le respect du registre de langue et le style"
        }

    def evaluate_text(self, text: str, context: str) -> List[Dict]:
        """
        Evaluate student text based on multiple rubrics.
        Returns a list of dictionaries containing scores and feedback for each rubric.
        """
        evaluations = []
        
        for rubric_name, rubric_description in self.rubrics.items():
            prompt = f"""
            Veuillez évaluer le texte suivant selon le critère : {rubric_name}
            {rubric_description}
            
            L'évaluation devra prendre en compte le contexte: {context}
            Texte à évaluer :
            "{text}"
            
            Fournissez :
            1. Note (sur une échelle de 1 à 4, où 1 = insuffisant, 2 = suffisant, 3 = bien, 4 = excellent)
            2. Commentaire détaillé
            
            Format de réponse :
            Note: [nombre]
            Commentaire: [votre feedback]
            """
            

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
           
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Vous êtes un évaluateur expérimenté en langue française."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                )

                result = response.choices[0].message.content
                logger.info(result)
                # Parse response
                score_line = result.split('\n')[0]
                feedback_line = ' '.join(result.split('\n')[1:])

                score = int(score_line.split(':')[1].strip())
                feedback = feedback_line.split(':')[1].strip()

                # Ensure score is between 1 and 4
                score = max(1, min(4, score))
                logger.info(score, feedback)
                evaluations.append({
                    "rubric": rubric_name,
                    "score": score,
                    "feedback": feedback
                })

            except Exception as e:
                evaluations.append({
                    "rubric": rubric_name,
                    "score": 0,
                    "feedback": f"Erreur pendant l'évaluation: {str(e)}"
                })
        return evaluations

def get_overall_score(evaluations: List[Dict]) -> float:
    """Calculate the overall score from all rubrics."""
    valid_scores = [eval_["score"] for eval_ in evaluations if eval_["score"] > 0]
    if not valid_scores:
        return 0
    return sum(valid_scores) / len(valid_scores)

# Example usage
if __name__ == "__main__":
    api_key=os.getenv("OPENAI_API_KEY")
    evaluator = TextEvaluator(api_key)
    
    sample_text = """
    L'impact du changement climatique sur les écosystèmes mondiaux est devenu 
    de plus en plus évident ces dernières années. La hausse des températures 
    a entraîné des changements significatifs dans les modèles météorologiques, 
    affectant la flore et la faune mondiale.
    """
    context = ""
    
    evaluations = evaluator.evaluate_text(sample_text, context)
    overall_score = get_overall_score(evaluations)
    
    print(f"Note globale: {overall_score:.2f}/4\n")
    print("Évaluations détaillées:")
    for eval_ in evaluations:
        print(f"\n{eval_['rubric'].upper()}:")
        print(f"Note: {eval_['score']}/4")
        print(f"Commentaire: {eval_['feedback']}")