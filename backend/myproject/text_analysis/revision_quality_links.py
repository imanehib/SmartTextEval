#ATTENDRE VALIDATION DE VANDA ET FRANÇOIS pour le coder

"""

def analyze_process_report(graph_info):
    # Analyze the process report to extract relevant information for generating feedback
    # we need to divide the report into three equal parts (in terms of timestamps)
    # we need to count the revisions in each part and their type
    total_time = graph_info[-1]['end'] - graph_info[0]['start']
    part_duration = total_time / 3

    analysis = {
        "part_1": {"duration": part_duration, "revisions": []},
        "part_2": {"duration": part_duration, "revisions": []},
        "part_3": {"duration": part_duration, "revisions": []}
    }

    for item in graph_info:
        if item['type'] == 'Meaning-oriented' or item['type'] == 'Surface':
            if item['start'] < graph_info[0]['start'] + part_duration:
                analysis["part_1"]["revisions"].append(item)
            elif item['start'] < graph_info[0]['start'] + 2 * part_duration:
                analysis["part_2"]["revisions"].append(item)
            else:
                analysis["part_3"]["revisions"].append(item)

    return analysis

def count_revision_types(analysis, part, type):
    return sum(1 for item in analysis[part]["revisions"] if item['type'] == type)

def generate_global_feedback(llm_evaluation, process_report, analysis):

    for eval in llm_evaluation:
        if eval['score']<=2:
            rubric=eval['rubric']
            if rubric=="organisation" or  rubric=="réponse_consigne" or rubric=="arguments":
                  if analysis["part_1"]["Meaning-oriented"] <
            elif rubric=="vocabulaire":
                  #
            elif rubric=="grammaire":
                  #
            elif rubric=="orthographe":
                  #
            elif rubric=="style":
                  #
"""