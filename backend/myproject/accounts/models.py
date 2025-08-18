from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    STUDENT = 'student'
    PROFESSOR = 'professor'
    ROLE_CHOICES = (
        (STUDENT, 'Étudiant'),
        (PROFESSOR, 'Professeur'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, null=True)

    age = models.PositiveIntegerField(null=True, blank=True)
    study_level = models.CharField(max_length=50, null=True, blank=True)

    teaching_subject = models.CharField(max_length=100, null=True, blank=True)

    n_annotated = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username
