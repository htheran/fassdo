
# Create your views here.
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Playbook
from .forms import PlaybookForm

# Crear un nuevo playbook
def create_playbook(request):
    if request.method == 'POST':
        form = PlaybookForm(request.POST, request.FILES)
        if form.is_valid():
            playbook = form.save(commit=False)

            # Obtener tipo y sistema operativo
            playbook_type = form.cleaned_data.get('playbook_type')
            operating_system = form.cleaned_data.get('operating_system')

            # Determinar la ruta de almacenamiento según el tipo y el sistema operativo
            subfolder = os.path.join('playbooks', playbook_type, operating_system)
            full_path = os.path.join(settings.MEDIA_ROOT, subfolder)

            # Crear la carpeta si no existe
            os.makedirs(full_path, exist_ok=True)

            # Guardar el archivo en la carpeta correspondiente
            playbook_file = request.FILES['playbook_file']
            playbook_file_path = os.path.join(full_path, playbook_file.name)

            # Guardar el archivo en el sistema de archivos
            with open(playbook_file_path, 'wb+') as destination:
                for chunk in playbook_file.chunks():
                    destination.write(chunk)

            # Asignar la ruta del archivo al playbook
            playbook.playbook_file.name = os.path.join(subfolder, playbook_file.name)
            playbook.save()

            return redirect('playbook_list')

    else:
        form = PlaybookForm()

    return render(request, 'playbook/create_playbook.html', {'form': form})


# Editar un playbook existente
def edit_playbook(request, pk):
    playbook = get_object_or_404(Playbook, pk=pk)
    if request.method == 'POST':
        form = PlaybookForm(request.POST, request.FILES, instance=playbook)
        if form.is_valid():
            form.save()
            return redirect('playbook_list')
    else:
        form = PlaybookForm(instance=playbook)
    return render(request, 'playbook/edit_playbook.html', {'form': form})

# Eliminar un playbook
def delete_playbook(request, pk):
    playbook = get_object_or_404(Playbook, pk=pk)
    if request.method == 'POST':
        playbook.delete()
        return redirect('playbook_list')
    return render(request, 'playbook/delete_playbook.html', {'playbook': playbook})

# Listar playbooks
def list_playbooks(request):
    playbooks = Playbook.objects.all()
    return render(request, 'playbook/list_playbooks.html', {'playbooks': playbooks})
