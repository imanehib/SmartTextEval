from django.urls import path
from .views import home, save_text
from .views import home, delete_text,update_typing_data,update_list,save_user_typing
from django.contrib import admin
from .views import save_typing_event
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', home, name='home'),  # Page principale
    path('save/', save_text, name='save_text'),  # Route pour sauvegarder
    path('delete_text/<int:text_id>/', delete_text, name='delete_text'),
    #path('save-typing/', save_typing, name='save_typing'),
    path('update_typing_data/', update_typing_data, name='update_typing_data'),
    path('update_list/', update_list, name='update_list'),  # URL pour l'AJAX
    path('admin/', admin.site.urls),  # Vérifie que cette ligne est présente
    path('save-user-typing/', save_user_typing, name='save_user_typing'),
    path("save_typing_event/", save_typing_event, name="save_typing_event"),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', home, name='home'),

]



