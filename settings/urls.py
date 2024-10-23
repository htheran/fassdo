from django.urls import path
from . import views

urlpatterns = [
    path('manage/', views.manage_settings, name='manage_settings'),
]
