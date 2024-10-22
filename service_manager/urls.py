from django.urls import path
from . import views

urlpatterns = [
    path('manage/', views.manage_services, name='manage_services'),
    path('host_status/', views.host_status, name='host_status'),  # Nueva ruta para host_status
   
]
