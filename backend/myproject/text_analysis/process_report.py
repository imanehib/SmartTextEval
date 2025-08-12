"""
Pour chaque nouveau texte qui arrive, on veut :
    extraire tous les débuts de révision
    extraire toutes les fins de révision associées

-> pas besoin de caractériser les features liés à l'état du texte à chaque frappe clavier donc pas besoin de reprendre explicitement le code existant : proposer une nouvelle version allégée

    caractériser les types de chaque révision à l'aide d'un LLM 
    créer un rapport de révision
"""

from typing import List
from ..text_analysis.revision import Revision
from ..text_analysis.revision_extraction import extract_revisions
from ..text_analysis.schemas import DecodedData
from celery import shared_task
from openai import OpenAI
import os


api_key = os.getenv("API_KEY")
client = OpenAI() 

@shared_task
def characterize_revisions(decoded_data: DecodedData)-> List[Revision]:
    """    Characterize revision in the decoded data.

    Args:
        decoded_data (DecodedData): The decoded data containing text and typing information.

    Returns:
        dict: A report containing classified revisions.
    """
    # Extract revisions from the decoded data
    revisions = extract_revisions(decoded_data.text_list, decoded_data.cursor_list)
    # Classify the revisions
    for revision in revisions:
        revision.classify(client, "asst_67wsBtBez3b89q7vK8K2LxXv")
    return revisions

def generate_process_report(revisions: List[Revision], decoded_data: DecodedData) -> dict:
    """Generate a process report from the classified revisions.
    This report will include simple indicators and information for the process graph
    Args:
        revisions (List[Revision]): List of classified revisions.
        
    """
    graph_info = []

    # 1. Collect all covered indices from all revisions
    covered_indices = set()
    for revision in revisions:
        covered_indices.update(range(revision.index_start, revision.index_end + 1))
        graph_info.append({
            "start": decoded_data.time_list[revision.index_start],
            "end": decoded_data.time_list[revision.index_end],
            "type": revision.type,
        })

    # 2. Identify and add writing periods
    writing_started = False
    start_time = None

    for index, time_point in enumerate(decoded_data.time_list):
        if index not in covered_indices:
            if not writing_started:
                # Start a new writing block
                start_time = time_point
                writing_started = True
        else:
            if writing_started:
                # End current writing block before current revision index
                end_time = decoded_data.time_list[index - 1] if index > 0 else time_point
                graph_info.append({
                    "start": start_time,
                    "end": end_time,
                    "type": "writing",
                })
                writing_started = False

    # 3. Handle trailing writing period at the end
    if writing_started:
        graph_info.append({
            "start": start_time,
            "end": decoded_data.time_list[-1],
            "type": "writing",
        })
        
    report = {
        "total_revisions": len(revisions),

        "graph_info": graph_info,  # List of Revision objects
    }
    return report
