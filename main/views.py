
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count, F
from django.db.models.functions import TruncDate
from inventory.models import Environment, Group, Host
from playbook.models import Playbook
from executor.models import ExecutionHistory


# Vista para el index (restringida a usuarios logueados)
@login_required
def index(request):
    # Total counts
    total_envs = Environment.objects.count()
    total_groups = Group.objects.count()
    total_hosts = Host.objects.count()

    redhat_hosts = Host.objects.filter(operating_system='Redhat').count()
    debian_hosts = Host.objects.filter(operating_system='Debian').count()
    windows_hosts = Host.objects.filter(operating_system='Windows').count()

    total_playbooks = Playbook.objects.count()
    playbooks_host = Playbook.objects.filter(playbook_type='host').count()
    playbooks_group = Playbook.objects.filter(playbook_type='group').count()

    redhat_playbooks = Playbook.objects.filter(operating_system='redhat').count()
    debian_playbooks = Playbook.objects.filter(operating_system='debian').count()
    windows_playbooks = Playbook.objects.filter(operating_system='windows').count()

    total_executions = ExecutionHistory.objects.count()

    most_used_playbook = ExecutionHistory.objects.values('playbook__name').annotate(playbook_count=Count('playbook')).order_by('-playbook_count').first()
    most_used_playbook_name = most_used_playbook['playbook__name'] if most_used_playbook else 'N/A'
    most_used_playbook_count = most_used_playbook['playbook_count'] if most_used_playbook else 0

    most_used_host = ExecutionHistory.objects.values('host__hostname').annotate(host_count=Count('host')).order_by('-host_count').first()
    most_used_group = ExecutionHistory.objects.values('group__name').annotate(group_count=Count('group')).order_by('-group_count').first()

    # Execution history for chart
    execution_data = (
        ExecutionHistory.objects
        .annotate(execution_date=TruncDate('date'))
        .values('execution_date')
        .annotate(count=Count('id'))
        .order_by('execution_date')
    )

    execution_dates = [entry['execution_date'].strftime('%Y-%m-%d') for entry in execution_data]
    execution_counts = [entry['count'] for entry in execution_data]
    


    # Obtener la IP privada y la fecha de login
    user_ip = request.META.get('REMOTE_ADDR')
    login_date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

    context = {
        'total_envs': total_envs,
        'total_groups': total_groups,
        'total_hosts': total_hosts,
        'redhat_hosts': redhat_hosts,
        'debian_hosts': debian_hosts,
        'windows_hosts': windows_hosts,
        'total_playbooks': total_playbooks,
        'playbooks_host': playbooks_host,
        'playbooks_group': playbooks_group,
        'redhat_playbooks': redhat_playbooks,
        'debian_playbooks': debian_playbooks,
        'windows_playbooks': windows_playbooks,
        'total_executions': total_executions,
        'most_used_playbook_name': most_used_playbook_name,
        'most_used_playbook_count': most_used_playbook_count,
        'most_used_host': most_used_host['host__hostname'] if most_used_host else 'N/A',
        'most_used_group': most_used_group['group__name'] if most_used_group else 'N/A',
        'execution_dates': execution_dates,
        'execution_counts': execution_counts,
        'user_ip': user_ip,
        'login_date': login_date,
    }

    return render(request, 'main/index.html', context)


# Vista para el login
def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
    
    else:
        form = AuthenticationForm()
    
    return render(request, 'main/login.html', {'form': form})

# Vista para el index (restringida a usuarios logueados)


# Vista para el logout
def user_logout(request):
    logout(request)
    return redirect('login')


