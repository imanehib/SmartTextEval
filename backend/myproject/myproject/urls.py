from django.contrib import admin
from django.urls import path,include
from myproject.text_analysis.views import home, save_text
from django.urls import path
from myproject.text_analysis.views import home, save_text
from myproject.text_analysis.views import home, delete_text,update_typing_data,update_list,save_user_typing
from django.contrib import admin
from myproject.text_analysis.views import save_typing_event
from django.urls import path
from myproject.text_analysis import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),  # Si c'est la page d'accueil
    path('analyze/', views.analyze, name='analyze'),  # Ajouter cette ligne pour l'URL analyze/
    path('save/', views.save_text, name='save_text'),
    path('delete_text/<int:text_id>/', views.delete_text, name='delete_text'),
    path('update_typing_data/', views.update_typing_data, name='update_typing_data'),
    path('update_list/', views.update_list, name='update_list'),
    path('admin/', admin.site.urls),
    path('save-user-typing/', views.save_user_typing, name='save_user_typing'),
    path('save_typing_event/', views.save_typing_event, name='save_typing_event'),
    #path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    ##path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #path('signup/', views.signup, name='signup'),
    path('', views.home, name='home'),
]
