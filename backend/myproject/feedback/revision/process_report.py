"""
Pour chaque nouveau texte qui arrive, on veut :
    extraire tous les débuts de révision
    extraire toutes les fins de révision associées

-> pas besoin de caractériser les features liés à l'état du texte à chaque frappe clavier donc pas besoin de reprendre explicitement le code existant : proposer une nouvelle version allégée

    caractériser les types de chaque révision à l'aide d'un LLM 
    créer un rapport de révision
"""

from typing import List
from revision.revision import Revision
from revision.revision_extraction import extract_revisions
from text_analysis.schemas import DecodedData
from openai import OpenAI
import os





client = OpenAI() 

def characterize_revisions(decoded_data: DecodedData)-> List[Revision]:
    """    Characterize revision in the decoded data.

    Args:
        decoded_data (DecodedData): The decoded data containing text and typing information.

    Returns:
        dict: A report containing classified revisions.
    """
    # Extract revisions from the decoded data
    revisions = extract_revisions(decoded_data.text_list, decoded_data.cursor_list, decoded_data.time_list, decoded_data.context)
    # Classify the revisions
    for revision in revisions:
        revision.classify(client, "asst_67wsBtBez3b89q7vK8K2LxXv")
    return revisions

def generate_process_report(revisions: List[Revision]) -> dict:
    """Generate a process report from the classified revisions.
    This report will include simple indicators
    Args:
        revisions (List[Revision]): List of classified revisions.
        
    """

