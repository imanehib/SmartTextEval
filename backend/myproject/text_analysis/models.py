
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
    text_progression = models.TextField()  # Évolution du texte
    timestamp = models.DateTimeField(auto_now_add=True)  # Date d'enregistrement
    action      = models.CharField(max_length=10, choices=[('insert','insert'),('delete','delete')])
    class Meta:
        ordering = ['timestamp']
    def __str__(self):
        return f"Event de {self.student} exo={self.exercise.id} pos={self.cursor_position} {self.action}"



