import json


def convert_answer_to_input(json_file, exercise_id, student_id):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Filter items where both exercise_id and student_id match
    filtered = [
        item for item in data
        if item.get("exercise_id") == exercise_id and item.get("student_id") == student_id
    ]

    text_list = [item.get("text", "") for item in filtered]
    time_list = [item.get("time", 0) for item in filtered]
    cursor_list = [item.get("cursor", 0) for item in filtered]
    final_text = text_list[-1] if text_list else ""
    context = "" #get instructions but not really useful
    text_type = "neutre"
    student_id = student_id
    exercise_id = exercise_id
    return final_text, text_list, time_list, cursor_list, context, text_type, student_id, exercise_id

