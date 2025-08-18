
from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Exercise(models.Model):
    author      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercises')
    title       = models.CharField(max_length=200)
    content     = models.TextField(default="")
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} par {self.author.username}"


class SavedText(models.Model):
    text = models.TextField()
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Ajoute ceci si ce champ n'est pas défini
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='teacher_assigned_texts')
    n_annotated = models.PositiveBigIntegerField()
    instructions = models.TextField(blank=True, null=True)  # Instructions pour l'exercice
    exercise = models.ForeignKey(Exercise, null=True, blank=True, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name='student_saved_texts')
    report_data = models.JSONField(null=True, blank=True)
    def __str__(self):
        return self.text[:50]  # Afficher un extrait du texte


class UserTyping(models.Model):
    session_id = models.CharField(max_length=255)
    cursor_position = models.IntegerField()
    text_progression = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Ce champ enregistre la date de création de l'objet

    def __str__(self):
        return self.session_id  # Tu peux afficher ce qui te convient ici


class TypingEvent(models.Model):
    cursor_position = models.PositiveIntegerField() # Position du curseur
    student     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise    = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    saved_text = models.ForeignKey('SavedText', on_delete=models.SET_NULL, null=True, blank=True)
    text_progression = models.TextField()  # Évolution du texte
    timestamp = models.FloatField() 
    action      = models.CharField(max_length=10, choices=[('insert','insert'),('delete','delete')])
    class Meta:
        ordering = ['timestamp']
    def __str__(self):
        return f"Event de {self.student} exo={self.exercise.id} pos={self.cursor_position} {self.action}"

class SavedAnnotation(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    annotation = models.JSONField(blank=True, null=True)  # Champ pour l'annotation

    def __str__(self):
        return f"Annotation de {self.user.username} pour l'exercice {self.exercise.title}"


class Questionnaire(models.Model):
    saved_text = models.ForeignKey(SavedText, on_delete=models.CASCADE, related_name="questionnaires", null=True)
    overall_approach = models.TextField()
    changes = models.TextField()
    clarity = models.CharField(max_length=10)
    organization = models.CharField(max_length=10)
    grammar = models.CharField(max_length=10)
    style = models.CharField(max_length=10)
    time_use = models.TextField()
    revision_continous = models.TextField()
    revision_improvements = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Questionnaire #{self.id} - {self.submitted_at.strftime('%Y-%m-%d')}"
    
