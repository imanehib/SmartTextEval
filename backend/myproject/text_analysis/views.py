import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from revision.process_report import characterize_revisions, generate_process_report
from .models import SavedText, Exercise , UserTyping , TypingEvent, SavedAnnotation
from .forms import ExerciseForm
from django.contrib.auth.decorators import login_required
import spacy
from spellchecker import SpellChecker
import re
import language_tool_python
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from .utils import compute_diff
from .schemas import DecodedData
from django.views.generic import ListView
from .models import TypingEvent
from language_tool_python import LanguageTool, LanguageToolPublicAPI
from language_tool_python.utils import LanguageToolError
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Exercise, SavedText



# Charger spaCy avec le modèle français
nlp = spacy.load("fr_core_news_sm")
# tool = language_tool_python.LanguageToolPublicAPI('fr')

_tool = None

def get_language_tool():
    """
    Renvoie un client LanguageTool configuré :
     - d’abord l’API publique (LanguageToolPublicAPI)
     - en cas d’erreur (quota expiré ou “Upgrade Required”), bascule sur
       votre instance locale lancée sur http://localhost:8081
    """
    global _tool
    if _tool is None:
        try:
            # essai de l'API publique
            _tool = LanguageToolPublicAPI('fr')
        except LanguageToolError:
            # fallback sur votre serveur local
            _tool = LanguageTool('fr', server_url='http://localhost:8081')
    return _tool

# Initialisation du correcteur orthographique
spell_checker = SpellChecker(language='fr')

def correct_text(text):
    """Corrige les fautes orthographiques, grammaticales et de conjugaison"""

    if not text.strip():
        return {"corrected_text": text, "score": 100, "suggestions": {}, "special_messages": []}

    # Séparer les phrases en tenant compte de la ponctuation
    sentences = re.split(r'([.!?])\s*', text)
    
    suggestions = {}
    special_messages = []
    corrected_sentences = []

    for i in range(0, len(sentences), 2):  # Parcours des phrases
        if i < len(sentences):
            sentence = sentences[i].strip()  
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""  

            # Vérification des majuscules AVANT tout
            words = re.findall(r"\w+|[.,!?;']", sentence)
            if words:
                first_word = words[0]
                if first_word[0].islower():
                    words[0] = first_word.capitalize()
                    special_messages.append(("La phrase doit commencer par une majuscule.", first_word))
                sentence = " ".join(words)  

            # Vérification avec LanguageTool pour grammaire et conjugaison
            matches = get_language_tool().check(sentence)

            
            for match in matches:
                error_word = match.context[match.offset:match.offset + match.errorLength]
                suggestion = match.replacements[0] if match.replacements else ""

                # Gestion des mots avec apostrophe, comme "m'appelle"
                if "'" in error_word:
                    parts = error_word.split("'")
                    if len(parts) == 2 and parts[0] in {"m", "t", "s", "l", "d", "n", "j"}:
                        # On ne vérifie que la partie après l'apostrophe
                        root_word = parts[1]
                        if root_word.lower() in spell_checker.unknown([root_word.lower()]):
                            corrected = spell_checker.correction(root_word.lower())
                            if corrected:
                                suggestions[root_word] = corrected
                                sentence = sentence.replace(root_word, corrected, 1)
                        continue  # On ne doit pas modifier "m'" par exemple, seulement la deuxième partie

                if suggestion and error_word.lower() != suggestion.lower():
                    suggestions[error_word] = suggestion
                    sentence = sentence.replace(error_word, suggestion, 1)

            # Vérification orthographique des autres mots
            words = re.findall(r"\w+|[.,!?;']", sentence)

            for j, word in enumerate(words):
                if word.isalpha() and "'" not in word:  
                    lower_word = word.lower()
                    if lower_word in spell_checker.unknown([lower_word]):  
                        corrected = spell_checker.correction(lower_word)
                        if corrected:
                            suggestions[word] = corrected
                            words[j] = corrected  

            # Reconstruction de la phrase corrigée
            corrected_sentence = " ".join(words) + punctuation
            corrected_sentences.append(corrected_sentence)

    # Reconstruction du texte corrigé
    corrected_text = " ".join(corrected_sentences)

    # Calcul du score
    total_words = sum(1 for w in corrected_text.split() if w.isalpha())
    incorrect_words = len(suggestions)
    score = max(0, 100 - (incorrect_words / total_words * 100)) if total_words else 100
    score = round(score, 2)

    return {
        "corrected_text": corrected_text,
        "score": score,
        "suggestions": suggestions,
        "special_messages": special_messages  
    }
    # 🔹 Corriger la majuscule au début de la phrase et après chaque ponctuation
    def capitalize_after_punctuation(text):
        # Mettre la première lettre en majuscule après une ponctuation, même sans espace
        text = re.sub(r'([.!?]\s*)(\w)', lambda x: x.group(1) + x.group(2).upper(), text)
        # Vérifier la première lettre du texte
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
            special_messages.append('La phrase devrait commencer par une majuscule.')
        return text

    # Corriger la capitalisation après chaque ponctuation
    corrected_text = capitalize_after_punctuation(corrected_text)

    # Calcul du score basé sur le nombre d'erreurs corrigées
    total_words = len(words)
    incorrect_words = len(suggestions)
    score = max(0, 100 - (incorrect_words / total_words * 100)) if total_words else 100
    score = round(score, 2)

    return {
        "corrected_text": corrected_text,
        "score": score,
        "suggestions": suggestions,
        "grammar_errors": grammar_errors,
        "special_messages": special_messages  # Ajout de messages spéciaux dans un champ séparé
    }

# text_analysis/views.py


@login_required
def home(request):
    # 1. Récupérer tous les exercices
    exercises = Exercise.objects.all()

    # 2. Récupérer, si présent, l'exercice sélectionné en GET
    exercise_id  = request.GET.get('exercise')
    exercise = None
    exercise_content = ''
    if exercise_id:
        try:
            exercise = Exercise.objects.get(pk=exercise_id)
            exercise_content = exercise.content
        except Exercise.DoesNotExist:
            exercise = None
            exercise_content = ''

    # 3. correction (POST)
    result = None
    saved_texts = SavedText.objects.all()  # Récupère tous les textes sauvegardés

    if request.method == "POST":
        text = request.POST.get('text', '').strip()
        instructions = request.POST.get("exercise_content", "")
        #list_position = request.POST.get('list_position', '')  # Récupère la position du curseur
        #list_progression = request.POST.get('list_progression', '')  # Récupère la progression du texte

        # Correction du texte
        #result = correct_text(text)

        # Sauvegarder dans la base de données
        if 'save' in request.POST:
            # Sauvegarder le texte, la position et la progression dans la base de données
            saved = SavedText.objects.create(
                text=text, 
                score=0,
                instructions=instructions,
                exercise_id = exercise_id,
                student_id=request.user.id
                #list_position=list_position, 
                #list_progression=list_progression
            )
             # Attach all relevant TypingEvents to this SavedText
            TypingEvent.objects.filter(
                student=request.user,
                exercise_id=exercise_id,
                saved_text__isnull=True  # optional: only those not yet linked
            ).update(saved_text=saved)

                    # Clear session (client-side must clear too, ideally via JS after successful form post)
            response = redirect('process_report', saved.id)
            response.set_cookie('clear_session_storage', '1', max_age=5)
            return response


    return render(request, 'home.html', {'exercises':    exercises, 'selected_id':  exercise_id, 'exercise': exercise, 'exercise_content': exercise_content, 'result': result, 'saved_texts': saved_texts})

def save_text(request):
    if request.method == "POST":
        instructions = request.POST.get("exercise_content", "")
        exercise_id = request.POST.get("exercise_id", None)  # Récupérer l'ID de l'exercice
        exercise = get_object_or_404(Exercise, pk=exercise_id)
        text = request.POST.get("text", "")
        score = 0
        saved = SavedText.objects.create(text=text, score=score, instructions=instructions, exercise = exercise, student=request.user)
         # Attach all relevant TypingEvents to this SavedText
        TypingEvent.objects.filter(
            student=request.user,
            exercise_id=exercise_id,
            saved_text__isnull=True  # optional: only those not yet linked
        ).update(saved_text=saved)
        return redirect('process_report', saved.id) 
    return JsonResponse({"error": "Méthode non autorisée"}, status=400)


def delete_text(request, text_id):
    text = get_object_or_404(SavedText, id=text_id)
    text.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'message': 'Texte supprimé avec succès!'})
    return redirect('text_analysis:home')


def update_typing_data(request):
    # Récupérer les données envoyées par la requête JavaScript
    text = request.POST.get('text', '')  # Le texte actuel
    cursor_position = int(request.POST.get('cursor_position', 0))  # Position du curseur
    
    # Si l'utilisateur a déjà des données de frappe dans la base
    user_typing_data, created = UserTyping.objects.get_or_create(user=request.user)

    # Mise à jour des listes dans le modèle
    user_typing_data.list_position.append(cursor_position)
    user_typing_data.list_progression.append(text)
    
    # Sauvegarde des changements dans la base de données
    user_typing_data.save()

    return JsonResponse({"message": "Données sauvegardées avec succès"}, status=200)



def update_list(request):
    if request.method == "POST":
        list_position = request.POST.get("list_position")  # Récupérer les données envoyées
        list_progression = request.POST.get("list_progression")

        # Mettre à jour ou ajouter les données dans la base de données
        new_entry = SavedText(list_position=list_position, list_progression=list_progression)
        new_entry.save()

        # Retourner une réponse JSON
        return JsonResponse({
            'success': True,
            'list_position': list_position,
            'list_progression': list_progression
        })
    return JsonResponse({'success': False})


# Supposons que tu aies une fonction d'analyse de texte
def analyze_text(text):
    # Ta logique d'analyse du texte ici
    # Retourne le texte corrigé ou les résultats de l'analyse
    return {
        'corrected_text': text,  # Juste un exemple, remplace cela par ta logique réelle
        'score': 85  # Exemple de score, à remplacer par ton propre calcul
    }

def analyze(request):
    if request.method == 'POST':
        # Récupérer les données envoyées par la requête
        text = request.POST.get('text', None)  # Si 'text' n'est pas trouvé, il renvoie None
        list_position = request.POST.get('list_position', '')  # Position du curseur
        list_progression = request.POST.get('list_progression', '')  # Progression du texte

        # Ajouter des logs pour vérifier les paramètres
        print(f"Texte reçu: {text}")
        print(f"Position du curseur: {list_position}")
        print(f"Progression du texte: {list_progression}")

        # Vérifier si 'text' est valide
        if not text or not isinstance(text, str):
            return JsonResponse({'error': 'Texte invalide ou vide'}, status=400)

        # Appeler la fonction correct_text pour analyser le texte
        result = correct_text(text)

        # Passer les résultats au template 'home.html' au lieu de renvoyer JSON
        return render(request, 'home.html', {
            'result': result,
            'list_position': list_position,
            'list_progression': list_progression
        })
    
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


def save_user_typing(request):
    if request.method == "POST":
        text = request.POST.get('text', '')
        cursor_position = request.POST.get('cursor_position', 0)
        session_id = request.user.username if request.user.is_authenticated else "anonymous"  # ✅ ligne ajoutée


        # Sauvegarde les frappes dans la base de données
        user_typing = UserTyping.objects.create(
            text=text,
            cursor_position=cursor_position,
            session_id=session_id,
        )
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'})

@csrf_exempt  # Désactiver temporairement CSRF pour le test
def save_typing_event(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            session_id = data.get("session_id")
            cursor_position = data.get("cursor_position")
            text_progression = data.get("text_progression")

            # Sauvegarder l'événement de frappe
            typing_event = UserTyping(
                session_id=session_id,
                cursor_position=cursor_position,
                text_progression=text_progression
            )
            typing_event.save()

            return JsonResponse({"message": "Frappes enregistrées !"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": "Méthode non autorisée"}, status=405)

@login_required
def add_exercise(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            ex = form.save(commit=False)
            ex.author = request.user
            ex.save()
            return redirect('accounts:professor_dashboard')
    else:
        form = ExerciseForm()
    return render(request, 'text_analysis/add_exercise.html', {'form': form})

@login_required
def delete_exercise(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)

    if not hasattr(request.user, 'role') or request.user.role != 'professor':
        return HttpResponseForbidden("Accès réservé aux professeurs.")
    
    if exercise.author != request.user:
        return HttpResponseForbidden("Vous n'avez pas le droit de supprimer cet exercice")
    
    if request.method == 'POST':
        exercise.delete()
        messages.success(request, "Exercice supprimé avec succès.")
    
    return redirect('accounts:professor_dashboard')


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
import json
from datetime import datetime
from .models import TypingEvent, Exercise
from .schemas import DecodedData
from .utils import compute_diff

@method_decorator(csrf_exempt, name='dispatch')
class SaveTypingDataView(View):
    def post(self, request, *args, **kwargs):
        print("Requête POST reçue pour save_typing_data")

        if not request.user.is_authenticated:
            print("Utilisateur non authentifié")
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        try:
            data = DecodedData.parse_raw(request.body)
            print(f"Données décodées : {data}")
        except Exception as e:
            print(f"Erreur de parsing JSON: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)

        try:
            exo = Exercise.objects.get(pk=data.exercise_id)
            print(f"Exercice trouvé : {exo}")
        except Exercise.DoesNotExist:
            print("Exercice introuvable")
            return JsonResponse({'error': 'Exercise not found'}, status=404)

        user = request.user

        events = []
        prev = None  # pour identifier la toute première itération
        for ts_ms, txt, cur in zip(data.time_list, data.text_list, data.cursor_list):
            try:
                if prev is None:
                    diff = {'action': 'insert'}  # première itération, on considère comme insertion
                else:
                    diff = compute_diff(prev, txt)
                    if diff['action'] == 'skip':
                        prev = txt
                        continue
                    print(f"Diff trouvé: {diff}")

                event = TypingEvent(
                    student         = user,
                    exercise       = exo,
                    timestamp       = ts_ms / 1000,
                    cursor_position = int(cur),
                    action          = diff['action'],
                    text_progression= txt,
                )
                events.append(event)
                prev = txt  # mise à jour ici à chaque tour !

            except Exception as e:
                print(f"Erreur pendant compute_diff: {str(e)}")



        if events:
            TypingEvent.objects.bulk_create(events)
            print(f"{len(events)} événements enregistrés")
            return JsonResponse({'status': 'success', 'saved_events': len(events)})
        else:
            print("Aucun événement à enregistrer")
            return JsonResponse({'error': 'No events created'}, status=400)




class TypingEventListView(ListView):
    model = TypingEvent
    template_name = 'text_analysis/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return (super()
                .get_queryset()
                .select_related('student', 'exercise')
                .order_by('-timestamp'))
    
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from collections import defaultdict
import json
from .models import TypingEvent
from .schemas import DecodedData

@login_required
def export_typingevents_for_student(request):
    student_id = request.user.id

    # On récupère tous les événements de l'utilisateur, triés par exercice et par timestamp
    events = TypingEvent.objects.filter(student_id=student_id).order_by('exercise_id', 'timestamp')

    if not events.exists():
        return JsonResponse({'message': 'Aucune frappe trouvée pour cet utilisateur.'}, status=404)

    # On regroupe par exercice
    sessions = defaultdict(list)
    for ev in events:
        sessions[ev.exercise_id].append(ev)

    all_sessions_data = []

    for exercise_id, ev_list in sessions.items():
        exercise = ev_list[0].exercise  # On suppose tous les events ont le même exercice
        time_list = [int(ev.timestamp.timestamp() * 1000) for ev in ev_list]
        text_list = [ev.text_progression for ev in ev_list]
        cursor_list = [str(ev.cursor_position) for ev in ev_list]

        data = DecodedData(
            final_text=text_list[-1],
            context=exercise.content or "",
            text_type="",
            time_list=time_list,
            text_list=text_list,
            cursor_list=cursor_list,
            student_id=str(student_id),
            exercise_id=str(exercise_id)
        )
        all_sessions_data.append(data.dict())

    json_data = json.dumps(all_sessions_data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_data, content_type='application/json; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename=typingevents_student_{student_id}.json'
    return response


@login_required
def annotate_view(request):
    
    if request.method == 'POST':
        text = request.POST.get('text', '')
        grades = []
        for i in range(1, 5):
            grade = request.POST.get(f'grade{i}')
            if not grade:
                messages.error(request, "Tous les critères doivent être notés.")
                return redirect('text_analysis:annotate_view')
            grades.append(grade)

        annotation = "|".join(grades)

        if not text or not annotation:
            messages.error(request, "Le texte et l'annotation ne peuvent pas être vides.")
            return redirect('text_analysis:annotate_view')

        SavedAnnotation.objects.create(
            student=request.user,
            text=text,
            annotation=annotation
        )
        messages.success(request, "Annotation sauvegardée avec succès.")
        return redirect('text_analysis:annotate_view')
    else:
        my_text = get_object_or_404(SavedText, pk=49)#change the pk to the one you want to annotate
        labels = ["Clarté", "Organisation", "Pertinence", "Orthographe"]
        context = {'text': my_text.text, 'labels': labels}
        
        #annotations = SavedAnnotation.objects.filter(exercise=exercise).order_by('-created_at')
        return render(request, 'text_analysis/annotate.html', context)
    

@login_required
def process_report_view(request, id):
    
    if request.method == 'GET':
        my_text = get_object_or_404(SavedText, id=id)
        print(my_text)
        keystrokes = TypingEvent.objects.filter(saved_text=id).order_by('id')
        time_list = [k.timestamp for k in keystrokes]
        text_list = [k.text_progression for k in keystrokes]
        cursor_list = [k.cursor_position for k in keystrokes]
        # On peut ajouter des logs pour vérifier les données
        print(f"Text: {my_text.text}") 
        print(f"Instructions: {my_text.instructions}")
        print(f"Time List: {time_list}")
        print(f"Text List: {text_list}")
        print(f"User: {request.user.id}")
        print(f"Exercise ID: {my_text.exercise_id}")
        print(f"Text ID: {my_text.id}")
        decoded_data = DecodedData(
            final_text=my_text.text,
            context=my_text.instructions,
            text_type="",
            time_list=time_list,
            text_list=text_list,
            cursor_list=cursor_list,
            student_id=str(request.user.id),
            exercise_id=str(my_text.exercise_id),
            text_id=str(my_text.id)
        )
        revisions = characterize_revisions(decoded_data)
        report = generate_process_report(revisions)
        context = {'text': my_text.text, 'instructions': my_text.instructions, 'text_list': text_list, 'time_list': time_list, 'cursor_list': cursor_list, 'process_report': report} # TODO : handle multiple trials of the same exercise
        return render(request, 'text_analysis/process_report.html', context)