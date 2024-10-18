from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.list_playbooks, name='playbook_list'),
    path('create/', views.create_playbook, name='create_playbook'),
    path('edit/<int:pk>/', views.edit_playbook, name='edit_playbook'),
    path('delete/<int:pk>/', views.delete_playbook, name='delete_playbook'),

    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
