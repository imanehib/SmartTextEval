from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class StudentSignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        required=True,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'placeholder': "Choisissez un nom d'utilisateur"}),
        help_text="Exemple : etudiant123"
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Prénom",
        widget=forms.TextInput(attrs={'placeholder': "Votre prénom"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Nom",
        widget=forms.TextInput(attrs={'placeholder': "Votre nom de famille"}),
    )
    email = forms.EmailField(
        required=True,
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={'placeholder': "exemple@domaine.com"}),
        help_text="Veuillez saisir une adresse e-mail valide."
    )
    age = forms.IntegerField(
        required=True,
        label="Âge",
        widget=forms.NumberInput(attrs={'placeholder': "Votre âge"}),
    )
    study_level = forms.CharField(
        max_length=50,
        required=True,
        label="Niveau d'études",
        widget=forms.TextInput(attrs={'placeholder': "Exemple : Baccalauréat, Licence, Master"}),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Ici, nous incluons les champs souhaités pour un étudiant.
        fields = ('username', 'first_name', 'last_name', 'email', 'age', 'study_level')


class ProfessorSignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        required=True,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'placeholder': "Choisissez un nom d'utilisateur"}),
        help_text="Exemple : professeur456"
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Prénom",
        widget=forms.TextInput(attrs={'placeholder': "Votre prénom"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Nom",
        widget=forms.TextInput(attrs={'placeholder': "Votre nom de famille"}),
    )
    email = forms.EmailField(
        required=True,
        label="Adresse e-mail",
        widget=forms.EmailInput(attrs={'placeholder': "exemple@domaine.com"}),
        help_text="Veuillez saisir une adresse e-mail valide."
    )
    teaching_subject = forms.CharField(
        max_length=100,
        required=True,
        label="Matière enseignée",
        widget=forms.TextInput(attrs={'placeholder': "La matière que vous enseignez"}),
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # champs souhaités pour un professeur
        fields = ('username', 'first_name', 'last_name', 'email', 'teaching_subject')
