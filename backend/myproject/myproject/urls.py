from django.contrib import admin
from django.urls import path, include
from myproject.text_analysis import views
from myproject.accounts.views import index 
#from django.contrib.auth import views 



urlpatterns = [
    path('', index, name='index'),  # page d'accueil
    path('text-analysis/', include('myproject.text_analysis.urls', namespace='text_analysis')),
    path('delete_text/<int:text_id>/', views.delete_text, name='delete_text'),
    path('update_typing_data/', views.update_typing_data, name='update_typing_data'),
    path('update_list/', views.update_list, name='update_list'),
    path('admin/', admin.site.urls),
    path('accounts/', include('myproject.accounts.urls', namespace='accounts')),
    path('process_report/<int:id>', views.process_report_view, name='process_report'),
    #path('', views.home, name='home'),
]
