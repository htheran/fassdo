# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('manage/', views.manage_settings, name='manage_settings'),
    path('manage/<int:setting_id>/', views.manage_settings, name='edit_setting'),
    path('delete/<int:setting_id>/', views.delete_setting, name='delete_setting'),
]
