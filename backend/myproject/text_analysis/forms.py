from django import forms
from .models import Exercise

class ExerciseForm(forms.ModelForm):
    class Meta:
        model  = Exercise
        fields = ['title', 'content', 'session']
        widgets = {
            'title':   forms.TextInput(attrs={'placeholder': "Titre de l'exercice"}),
            'content': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': "Entrez ici l’énoncé…",
                'style': 'font-family: monospace;'
            }),
            'session' : forms.NumberInput(attrs={'placeholder': "Entrez ici le numéro de session correspondant à l'exercice"}),
        }
        labels = {
            'title':   "Titre",
            'content': "Énoncé de l’exercice",
            'session': "Session d'expérimentation"
        }
