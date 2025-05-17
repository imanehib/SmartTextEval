from django.urls import path
from . import views
from .views import (
    CustomLoginView,
    CustomLogoutView,
    signup_choice,
    student_signup,
    professor_signup,
    professor_dashboard
)

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', signup_choice, name='signup_choice'),
    path('signup/student/', student_signup, name='student_signup'),
    path('signup/professor/', professor_signup, name='professor_signup'),
    path('professor-dashboard/', professor_dashboard, name='professor_dashboard'),
]
