from django import forms
from .models import Exercise

class ExerciseForm(forms.ModelForm):
    class Meta:
        model  = Exercise
        fields = ['title', 'content']
        widgets = {
            'title':   forms.TextInput(attrs={'placeholder': "Titre de l'exercice"}),
            'content': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': "Entrez ici l’énoncé…",
                'style': 'font-family: monospace;'
            }),
        }
        labels = {
            'title':   "Titre",
            'content': "Énoncé de l’exercice",
        }
