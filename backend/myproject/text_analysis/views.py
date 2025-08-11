import json
import threading
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from ..text_analysis.process_report import characterize_revisions, generate_process_report



from .models import Questionnaire, SavedText, Exercise , UserTyping , TypingEvent, SavedAnnotation
from .forms import ExerciseForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.views import View
from django.urls import reverse
from django.utils.decorators import method_decorator
from .utils import compute_diff
from .schemas import DecodedData
from django.views.generic import ListView
from .models import TypingEvent
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Exercise, SavedText
import json
from django.contrib.auth.decorators import login_required 
from django.core.cache import cache
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





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



    return render(request, 'home.html', {'exercises':    exercises, 'selected_id':  exercise_id, 'exercise': exercise, 'exercise_content': exercise_content, 'result': result, 'saved_texts': saved_texts})




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
        saved = SavedText.objects.create(
            text=data.final_text,
            score=0,
            instructions=data.context,
            exercise_id = data.exercise_id,
            student_id=request.user.id
            )
        events = []
        prev = None  # pour identifier la toute première itération
        for ts_ms, txt, cur in zip(data.time_list, data.text_list, data.cursor_list):

            try:
                if prev is None:
                    diff = {'action': 'insert'}  # première itération, on considère comme insertion
                else:
                    #diff = compute_diff(prev, txt)
                    #if diff['action'] == 'skip':
                    #    prev = txt
                    #    continue
                    #print(f"Diff trouvé: {diff}")
                    diff['action'] = "skip"
                event = TypingEvent(
                    student         = user,
                    exercise       = exo,
                    timestamp       = ts_ms / 1000,
                    cursor_position = int(cur),
                    action          = diff['action'],
                    text_progression= txt,
                    saved_text      = saved
                )
                events.append(event)
                prev = txt  # mise à jour ici à chaque tour !

            except Exception as e:
                print(f"Erreur pendant compute_diff: {str(e)}")



        if events:
            TypingEvent.objects.bulk_create(events)

            # Start background analysis thread here
            threading.Thread(
                target=run_analysis_in_background,
                args=(saved.id, user.id),
                daemon=True  # optional but recommended
            ).start()

            # Return the URL to the questionnaire page, passing the saved text ID in session or query param
            request.session['text_id'] = saved.id
            questionnaire_url = reverse('questionnaire')

            return JsonResponse({
                'status': 'success',
                'saved_events': len(events),
                'redirect_url': questionnaire_url
            })

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
    
"""
@login_required
def process_report_view(request, id):
    
    if request.method == 'GET':
        cache_key = f'process_report_{id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            print("Données récupérées du cache")
            return render(request, 'text_analysis/process_report.html', cached_data)
        

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
        report = generate_process_report(revisions, decoded_data)
        context = {'text': my_text.text, 'instructions': my_text.instructions, 'text_list': text_list, 'time_list': time_list, 'cursor_list': cursor_list, 'process_report': report, 'graph_info': report.get("graph_info", [])} # TODO : handle multiple trials of the same exercise
        cache.set(cache_key, context, timeout=86400)
        #return render(request, 'text_analysis/process_report.html', context)
        return redirect('questionnaire')"""

@login_required
def process_report_view(request, id):
    cache_key = f'process_report_{id}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return render(request, 'text_analysis/process_report.html', cached_data)

    my_text = get_object_or_404(SavedText, id=id)
    if my_text.analysis_report:
        # Build context from saved report
        context = {
            'text': my_text.text,
            'instructions': my_text.instructions,
            'process_report': my_text.analysis_report,
            # You may want to reconstruct time_list, text_list, cursor_list if you saved them
            # or skip them if not needed for rendering.
            'graph_info': my_text.analysis_report.get("graph_info", [])
        }
        cache.set(cache_key, context, timeout=86400)
        return render(request, 'text_analysis/process_report.html', context)

    # Still processing or no data — show waiting page
    return render(request, 'text_analysis/waiting.html', {'text_id': id})


def run_analysis_in_background(id, user_id):
    my_text = SavedText.objects.get(id=id)
    keystrokes = TypingEvent.objects.filter(saved_text=id).order_by('id')
    time_list = [k.timestamp for k in keystrokes]
    text_list = [k.text_progression for k in keystrokes]
    cursor_list = [k.cursor_position for k in keystrokes]

    decoded_data = DecodedData(
        final_text=my_text.text,
        context=my_text.instructions,
        text_type="",
        time_list=time_list,
        text_list=text_list,
        cursor_list=cursor_list,
        student_id=str(user_id),
        exercise_id=str(my_text.exercise_id),
        text_id=str(my_text.id)
    )
    revisions = characterize_revisions(decoded_data)
    report = generate_process_report(revisions, decoded_data)

    cache_key = f'process_report_{id}'
    context = {
        'text': my_text.text,
        'instructions': my_text.instructions,
        'text_list': text_list,
        'time_list': time_list,
        'cursor_list': cursor_list,
        'process_report': report,
        'graph_info': report.get("graph_info", [])
    }
        # Save report in DB
    my_text.analysis_report = report
    my_text.save()
    cache.set(cache_key, context, timeout=86400)
    

def submit_questionnaire(request):
    if request.method == 'POST':
        text_id = request.session.get('text_id')
        if not text_id:
            return HttpResponse("No associated text found.", status=400)

        saved_text = get_object_or_404(SavedText, pk=text_id)
        # Create a new Questionnaire entry
        Questionnaire.objects.create(
            saved_text=saved_text,
            overall_approach=request.POST.get('overall_approach', ''),
            changes=request.POST.get('changes', ''),
            clarity=request.POST.get('clarity', ''),
            organization=request.POST.get('organization', ''),
            grammar=request.POST.get('grammar', ''),
            style=request.POST.get('style', ''),
            time_use=request.POST.get('time_use', ''),
            revision_continuous=request.POST.get('revision_continuous', ''),
            revision_improvements=request.POST.get('revision_improvements', ''),
        )
        return redirect('process_report', id=request.session.get('text_id'))  

    return render(request, 'questionnaire_form.html')

#small API for the waiting html page
@login_required
def analysis_status_api(request, id):
    status = cache.get(f'analysis_status_{id}', 'not_found')
    return JsonResponse({'status': status})