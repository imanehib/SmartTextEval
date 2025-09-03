

thresholds = {
    "Meaning-oriented-semantic-part": 2,
    "Meaning-oriented-semantic": 5,
    "Surface": 8,
    "Lexical": 4,
    "rubrics": 2
}

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
        if 'Meaning-oriented' in item['type'] or 'Surface' in item['type'] or 'Lexical' in item['type']:
            if item['start'] < graph_info[0]['start'] + part_duration:
                analysis["part_1"]["revisions"].append(item)
            elif item['start'] < graph_info[0]['start'] + 2 * part_duration:
                analysis["part_2"]["revisions"].append(item)
            else:
                analysis["part_3"]["revisions"].append(item)

    return analysis

def count_revision_types(analysis, part, type):
    return sum(1 for item in analysis[part]["revisions"] if type in item['type'])

def generate_global_feedback(llm_evaluation, analysis):
    feedbacks = []
    
    for eval in llm_evaluation:
        rubric = eval['rubric']
        score = eval['score']
        
        # Determine quality level
        quality_level = "quality_weak" if score <= thresholds["rubrics"] else "quality_strong"
        
        # Get revision counts
        revision_counts = _get_revision_counts(analysis, rubric)
        
        # Determine revision pattern
        revision_pattern = _determine_revision_pattern(revision_counts, rubric)
        
        # Generate feedback
        feedback_content = feedback_json[quality_level][rubric].get(revision_pattern, "")
        
        feedbacks.append({
            "rubric": rubric,
            "content": feedback_content
        })
    
    return feedbacks

def _get_revision_counts(analysis, rubric):
    """Get revision counts based on rubric type."""
    if rubric in ["organisation", "réponse_consigne", "arguments"]:
        revision_type = "Meaning-oriented"
    elif rubric == "vocabulaire":
        revision_type = "Lexical"
    else:  # grammaire, orthographe
        revision_type = "Surface"
    
    return {
        "total": sum(count_revision_types(analysis, part, revision_type) 
                    for part in ["part_1", "part_2", "part_3"]),
        "part_1": count_revision_types(analysis, "part_1", revision_type),
        "part_3": count_revision_types(analysis, "part_3", revision_type)
    }

def _determine_revision_pattern(revision_counts, rubric):
    """Determine the revision pattern based on counts."""
    # For surface-level revisions (grammaire, orthographe)
    if rubric in ["grammaire", "orthographe"]:
        if revision_counts["total"] < thresholds["Surface"]:
            return "few_revisions"
        else:
            return "many_revisions"
        # Note: burst_cuts logic to complete
    
    # For lexical revisions
    elif rubric == "vocabulaire":
        if revision_counts["total"] < thresholds["Lexical"]:
            return "few_revisions"
        else:
            return "many_revisions"
    
    # For meaning-oriented revisions
    else:
        if revision_counts["total"] < thresholds["Meaning-oriented-semantic"]:
            return "few_revisions"
        elif revision_counts["part_3"] <= thresholds["Meaning-oriented-semantic-part"]:
            return "late_revisions"
        elif revision_counts["part_1"] < thresholds["Meaning-oriented-semantic-part"]:
            return "early_revisions"
        else:
            return "many_revisions"

"""
On a déjà le fb LLM
Comment ajouter celui ci au bout en gardant le tout lisible, compréhensible et actionnable pour l'étudiant?


FB LLM/prof sur la qualité du produit. Notre fb doit forcément porter uniquement sur le process.
Priorisation de critères sur d'autres? 
Ordre aléatoire? Ordre fixe?

S'assurer d'isoler ce qu'on veut observer. On veut voir si notre retour sur la révision a un impact sur : le comportement de révision, la qualité finale

groupe 1 : groupe contrôle
groupe 2 : réplication (process report)
groupe 3 : expérimentation (process report + feedback révision) -> on ajoute un feedback ACTIONNABLE sur le process
seule question, à quel niveau on l'implémente? selon moi, rédaction->questionnaire->évaluation par profs->process report->feedbacks sur critères accompagnés de fb révisions

"""


feedback_json= {
    "quality_weak":{
        "réponse_consigne":{
            "few_revisions": "Pendant l'écriture, relisez vos idées et essayer d'évaluer leur pertinence par rapport au sujet. Si elles s'en écartent, prenez le temps de les reformuler ou de revoir votre approche.",
            "many_revisions": "Vous avez pris le temps de retravailler vos idées pendant l'écriture, félicitations, c'est un bon réflexe ! Poursuivez ce travail en vous assurant que votre texte répond bien au sujet et est pertinent.",
            "late_revisions": "Il est important de relire votre travail à la fin du processus d'écriture. Cela vous permettra de repérer les incohérences et d'améliorer la qualité globale de votre texte.",
            "early_revisions": "Dès le début de l'écriture, prenez l'habitude de relire vos idées et de planifier les suivantes. Cela vous aidera à mieux structurer votre argumentation et à éviter les erreurs."
        },
        "arguments": {
            "few_revisions": "Pendant l'écriture, relisez vos idées et essayer d'évaluer la qualité de vos arguments. Pour les améliorer n'hésitez pas à ajouter des exemples, ou à envisager le point de vue opposé pour mieux le contrer.",
            "many_revisions": "Vous avez pris le temps de retravailler vos arguments, c'est un bon réflexe ! Assurez-vous qu'ils sont bien étayés par des exemples pertinents.",
            "late_revisions": "Il est important de relire vos arguments à la fin du processus d'écriture. Cela vous permettra de repérer les incohérences et d'améliorer la qualité globale de votre texte.",
            "early_revisions": "Dès le début de l'écriture, prenez l'habitude de relire vos arguments et de planifier les suivants. Cela vous aidera à mieux structurer votre argumentation et à éviter les erreurs."
        },
        "organisation":{
            "few_revisions": "Pendant l'écriture, relisez la structure de votre texte et assurez-vous qu'elle est logique. N'hésitez pas à réorganiser vos idées pour améliorer la clarté de votre argumentation.",
            "many_revisions": "Vous avez pris le temps de retravailler les idées de votre texte, c'est un bon réflexe ! Assurez-vous que chaque partie est bien liée et contribue à votre argumentation, n'hésitez pas à le réorganiser si besoin.",
            "late_revisions": "Il est important de vérifier l'organisation de votre texte à la fin du processus d'écriture. Cela vous permettra de repérer les incohérences et d'améliorer la qualité globale de votre texte.",
            "early_revisions": "Dès le début de l'écriture, prenez l'habitude de planifier l'organisation de votre texte. Cela vous aidera à mieux structurer votre argumentation et à éviter les erreurs."
        },
        "vocabulaire":{
            "few_revisions": "Pendant l'écriture, relisez votre vocabulaire et essayez d'enrichir vos choix de mots. N'hésitez pas à utiliser des synonymes ou des expressions plus précises pour améliorer la qualité de votre texte.",
            "many_revisions": "Vous avez pris le temps de retravailler votre vocabulaire, c'est un bon réflexe ! Assurez-vous que vos choix de mots sont pertinents et variés.",
        },
        "orthographe":{
            "few_revisions": "Il est important de relire votre texte pour repérer les fautes d'orthographe.",
            "many_revisions": "Vous avez pris le temps de corriger les fautes d'orthographe, c'est un bon réflexe ! Assurez-vous que votre texte est exempt de fautes.",
            "burst_cuts": "Vous avez tendance à corriger vos fautes d'orthographe et de grammaire à la volée. Essayez dans un premier temps de finir d'écrire votre idée puis revenez sur les fautes ensuite."
        },
        "grammaire":{
            "few_revisions": "Il est important de relire votre texte pour repérer les fautes de grammaire.",
            "many_revisions": "Vous avez pris le temps de corriger les fautes de grammaire, c'est un bon réflexe ! Assurez-vous que votre texte est exempt de fautes.",
            "burst_cuts": "Vous avez tendance à corriger vos fautes de grammaire à la volée. Essayez dans un premier temps de finir d'écrire votre idée puis revenez sur les fautes ensuite."
        },
        "style":{

        }

    },
    "quality_strong":{
        "réponse_consigne":{
            "few_revisions": "towrite",
            "many_revisions": "towrite",
            "late_revisions": "towrite",
            "early_revisions": "towrite"
        },
        "arguments": {
            "few_revisions": "towrite",
            "many_revisions": "towrite",
            "late_revisions": "towrite",
            "early_revisions": "towrite"
        },
        "organisation":{
            "few_revisions": "towrite",
            "many_revisions": "towrite",
            "late_revisions": "towrite",
            "early_revisions": "towrite"
        },
        "vocabulaire":{
            "few_revisions": "towrite",
            "many_revisions": "towrite",
        },
        "orthographe":{
            "few_revisions": "towrite",
            "many_revisions": "towrite",
            "burst_cuts": "towrite"
        },
        "grammaire":{
            "few_revisions": "towrite",
            "many_revisions": "towrite",
            "burst_cuts": "towrite"
        },
        "style":{

        }

    }
}