from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import StudentSignUpForm, ProfessorSignUpForm
from django.urls import reverse_lazy
from ..text_analysis.models import Exercise, SavedText
from django.http import HttpResponseForbidden

# Récupère le modèle utilisateur personnalisé
CustomUser = get_user_model()

def index(request):
    return render(request, 'index.html')

# Vue de connexion (Login)
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    def get_success_url(self):
        if self.request.user.role == 'professor':
            return reverse_lazy('accounts:professor_dashboard')
        elif self.request.user.role == 'student':
            return reverse_lazy('accounts:student_dashboard')
        return reverse_lazy('index')

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Vous pouvez transmettre un paramètre "role" si nécessaire
        context['role'] = self.request.GET.get('role', '')
        return context

# Vue de déconnexion (Logout)
class CustomLogoutView(LogoutView):
    next_page = '/'  # Redirige vers la page d'accueil après déconnexion

# Vue d'inscription pour étudiants
def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = CustomUser.STUDENT  # ou simplement 'student'
            user.save()
            login(request, user)
            return redirect('accounts:student_dashboard')  # ou une autre route adaptée
    else:
        form = StudentSignUpForm()
    return render(request, 'registration/student_signup.html', {'form': form})

# Vue d'inscription pour professeurs
def professor_signup(request):
    if request.method == 'POST':
        form = ProfessorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = CustomUser.PROFESSOR  # ou simplement 'professor'
            user.save()
            login(request, user)
            return redirect('accounts:professor_dashboard')
    else:
        form = ProfessorSignUpForm()
    return render(request, 'registration/professor_signup.html', {'form': form})

# choix : étudiant ou professeur
def signup_choice(request):
    return render(request, 'registration/signup_choice.html')

@login_required
def professor_dashboard(request):
    if request.user.role != 'professor':
        return HttpResponseForbidden("Accès interdit.")
    
    exercises = Exercise.objects.filter(author=request.user)
    return render(request, 'professor_dashboard.html', {
        'exercises': exercises
    })

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return HttpResponseForbidden("Accès interdit.")
    
    exercise = Exercise.objects.filter(session=request.user.session).first()


    saved_text = SavedText.objects.filter(exercise=exercise, student_id=request.user.id).first()
    if saved_text is not None:
        if saved_text.n_annotated >= 1:
            request.user.feedback_ready = request.user.session  # si l'annotation a été faite (sous-entend que l'analyse aussi) alors le feedback est prêt
        else:
            request.user.feedback_ready = 0
    else:
        request.user.feedback_ready = 0
    request.user.save()
    return render(request, 'student_dashboard.html')
