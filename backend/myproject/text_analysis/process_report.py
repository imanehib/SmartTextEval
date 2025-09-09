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

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) 
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
        covered_indices.update(range(revision.index_start, revision.index_end+1))
        graph_info.append({
            "start": decoded_data.time_list[revision.index_start],
            "end": decoded_data.time_list[revision.index_end],
            "type": revision.type,
            "reasoning": revision.reasoning,
            "startpoint": revision.start_point,
            "text_before": revision.text_before,
            "text_end": revision.text_end
        })

    # 2. Identify and add writing periods
    writing_started = False
    start_time = None

    for index, time_point in enumerate(decoded_data.time_list):
        if index not in covered_indices:
            if not writing_started:
                # Start a new writing block
                start_time = decoded_data.time_list[index-1] if index >0 else time_point
                writing_started = True
        else:
            if writing_started:
                # End current writing block before current revision index
                end_time = decoded_data.time_list[index]
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

    indicators = compute_indicators(revisions, decoded_data, graph_info)
    report = {
        "total_revisions": len(revisions),

        "graph_info": graph_info,  # List of Revision objects
        "indicators": indicators,
    }


    return report


def compute_indicators(revisions: List[Revision], decoded_data: DecodedData, graph_info) -> dict:
    prev_time = 0
    break_count = 0
    break_time = 0
    for time in decoded_data.time_list:
        if time-prev_time>2:
            break_count += 1
            break_time += time-prev_time
            graph_info.append({
                "start": prev_time,
                "end": time,
                "type": "break" 
            }) # est ce qu'on veut que les pauses soient affichées par dessus les phases déjà existantes ou est ce qu'on veut les incorporer dans le graph?
            # 
        prev_time = time
        
    deletion_count = sum(1 for revision in revisions if revision.reason_start == "deletion")
    insertion_count = sum(1 for revision in revisions if revision.reason_start == "move")
    # Calculate ratio of final text to total text processed
    final_text_length = len(decoded_data.text_list[-1]) if decoded_data.text_list else 0
    
    # Calculate total text processed by summing only newly added text at each iteration
    total_text_processed = 0
    if decoded_data.text_list:
        # First text is all new
        total_text_processed += len(decoded_data.text_list[0])
        # For subsequent texts, only count the difference
        for i in range(1, len(decoded_data.text_list)):
            current_length = len(decoded_data.text_list[i])
            previous_length = len(decoded_data.text_list[i-1])
            if current_length > previous_length:
                total_text_processed += current_length - previous_length
    
    ratio_process_product = (final_text_length / total_text_processed)*100 if total_text_processed > 0 else 0

    indicators = {
        "writing_time": sum([info["end"] - info["start"] for info in graph_info if info["type"] == "writing"]),
        "revision_count": len(revisions),
        "break_count": break_count,
        "break_time": break_time,
        "deletion_count": deletion_count,
        "insertion_count": insertion_count,
        "ratio_process_product": ratio_process_product
    }

    return indicators

