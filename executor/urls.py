# /opt/site/horeb/executor/urls.py
# /opt/site/horeb/executor/urls.py

from django.urls import path
from . import views

app_name = 'executor'

urlpatterns = [
    path('execute/', views.PlaybookExecuteView.as_view(), name='execute'),
    path('execute-group/', views.ExecutePlaybookGroupView.as_view(), name='execute_playbook_group'),
    path('execution-history/', views.execution_history, name='execution_history'),
    path('load-groups/', views.LoadGroupsView.as_view(), name='load_groups'),
    path('load-hosts/', views.LoadHostsView.as_view(), name='load_hosts'),
    path('load-playbooks/', views.LoadPlaybooksView.as_view(), name='load_playbooks'), 
    path('execution-detail/<int:pk>/', views.execution_detail, name='execution_detail'),

    # Nuevas rutas para programar ejecuciones
    path('schedule/', views.SchedulePlaybookHostView.as_view(), name='schedule'),
    path('schedule-group/', views.SchedulePlaybookGroupView.as_view(), name='schedule_group'),
    path('scheduled-execution-history/', views.ScheduledExecutionHistoryView.as_view(), name='scheduled_execution_history'),
]
