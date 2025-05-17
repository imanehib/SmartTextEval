from django.contrib import admin
from django.urls import path, include
#from myproject.text_analysis.views import home, save_text
#from myproject.text_analysis.views import home, save_text
#from myproject.text_analysis.views import delete_text,update_typing_data,update_list,save_user_typing
#from myproject.text_analysis.views import save_typing_event
from myproject.text_analysis import views
from myproject.accounts.views import index 
#from django.contrib.auth import views 



urlpatterns = [
    path('', index, name='index'),  # page d'accueil
    path('text-analysis/', include('myproject.text_analysis.urls', namespace='text_analysis')),
    path('analyze/', views.analyze, name='analyze'),  # Ajouter cette ligne pour l'URL analyze/
    path('save/', views.save_text, name='save_text'),
    path('delete_text/<int:text_id>/', views.delete_text, name='delete_text'),
    path('update_typing_data/', views.update_typing_data, name='update_typing_data'),
    path('update_list/', views.update_list, name='update_list'),
    path('admin/', admin.site.urls),
    path('save-user-typing/', views.save_user_typing, name='save_user_typing'),
    path('save_typing_event/', views.save_typing_event, name='save_typing_event'),
    path('accounts/', include('myproject.accounts.urls', namespace='accounts')),
    #path('', views.home, name='home'),
]
