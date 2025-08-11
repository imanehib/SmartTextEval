from django.urls import path
from .views import process_report_view, annotate_view, delete_text,update_typing_data,update_list, TypingEventListView, SaveTypingDataView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views



app_name = 'text_analysis' 

urlpatterns = [
    path('', views.home, name='home'),  
    path('delete_text/<int:text_id>/', delete_text, name='delete_text'),
    #path('save-typing/', save_typing, name='save_typing'),
    path('update_typing_data/', update_typing_data, name='update_typing_data'),
    path('update_list/', update_list, name='update_list'),  # URL pour l'AJAX
    path('admin/', admin.site.urls),  # Vérifie que cette ligne est présente
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('teacher/add-exercise/', views.add_exercise,     name='add_exercise'),
    path('teacher/delete-exercise/<int:pk>/', views.delete_exercise, name='delete_exercise'),
    path('save-typing/', SaveTypingDataView.as_view(), name='save_typing_data'),
    path('events/', TypingEventListView.as_view(), name='typing_event_list'),
    #path('export_all_sessions/', views.export_all_sessions_for_logged_student, name='export_all_sessions'),
    path('export_typingevents/', views.export_typingevents_for_student, name='export_typingevents'),
    path('annotate/', annotate_view, name='annotate_view'),
    path('process_report/', process_report_view, name='process_report'),
    path('questionnaire/', views.submit_questionnaire, name='submit_questionnaire'),
    path('analysis-status/<int:id>/', views.analysis_status_api, name='analysis_status_api'),

]



