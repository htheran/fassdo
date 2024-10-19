from django.urls import path
from . import views
from .views import create_host, success_view, error_view

urlpatterns = [
    path('environments/', views.list_environments, name='list_environments'),
    path('environments/create/', views.create_environment, name='create_environment'),
    path('environments/edit/<int:pk>/', views.edit_environment, name='edit_environment'),
    
    path('groups/', views.list_groups, name='list_groups'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/edit/<int:pk>/', views.edit_group, name='edit_group'),
    path('groups/delete/<int:pk>/', views.delete_group, name='delete_group'),
    
    path('hosts/', views.list_hosts, name='list_hosts'),
    path('hosts/create/', views.create_host, name='create_host'),
    path('hosts/edit/<int:pk>/', views.edit_host, name='edit_host'),
    path('hosts/delete/<int:pk>/', views.delete_host, name='delete_host'),
    path('success/', success_view, name='success_url'),  # Definición para success_url
    path('error/', error_view, name='error_url'),    

    #path('fingerprints/', views.list_fingerprints, name='list_fingerprints'),
]
