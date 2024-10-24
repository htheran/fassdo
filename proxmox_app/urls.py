from django.urls import path
from . import views

urlpatterns = [
    path('list_vms/', views.list_vms, name='list_vms'),
    path('start_vm/<int:vmid>/', views.start_vm, name='start_vm'),
    path('stop_vm/<int:vmid>/', views.stop_vm, name='stop_vm'),
    path('restart_vm/<int:vmid>/', views.restart_vm, name='restart_vm'),
    path('start_container/<int:vmid>/', views.start_container, name='start_container'),
    path('stop_container/<int:vmid>/', views.stop_container, name='stop_container'),
    path('restart_container/<int:vmid>/', views.restart_container, name='restart_container'),
    
    path('create_snapshot/', views.create_snapshot, name='create_snapshot'), 
    path('list_snapshots/<int:vmid>/', views.list_snapshots, name='list_snapshots'),
    path('delete_snapshot/<int:vmid>/<str:snapname>/', views.delete_snapshot, name='delete_snapshot'),
    
    path('create_vm/', views.create_vm, name='create_vm'),
    path('vms/create/', views.create_vm, name='create_vm'),
    path('resources/', views.list_resources, name='list_resources'),

    path('list_templates/', views.list_templates, name='list_templates'),
    path('deploy_template/<int:vmid>/', views.deploy_template, name='deploy_template'),
    path('deploy_template/<int:template_id>/', views.deploy_template, name='deploy_template'),
]

