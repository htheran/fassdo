from django.shortcuts import render, redirect
from proxmoxer import ProxmoxAPI
import json
import requests
from django.contrib import messages
from django.core.paginator import Paginator
import os

# Conexión global a Proxmox
proxmox = ProxmoxAPI('10.100.0.5', user='root@pam', password='Pr0l1ant', verify_ssl=False)



def list_vms(request):
    try:
        nodes = proxmox.nodes.get()
        qemu_vms_list = []
        lxc_vms_list = []

        for node in nodes:
            node_name = node['node']
            try:
                qemu_vms = proxmox.nodes(node_name).qemu.get()
                for vm in qemu_vms:
                    qemu_vms_list.append(vm)
            except Exception as qemu_error:
                print(f"Error obteniendo VMs QEMU del nodo {node_name}: {qemu_error}")

            try:
                lxc_vms = proxmox.nodes(node_name).lxc.get()
                for vm in lxc_vms:
                    lxc_vms_list.append(vm)
            except Exception as lxc_error:
                print(f"Error obteniendo contenedores LXC del nodo {node_name}: {lxc_error}")

        # Ordenar las listas por 'vmid' en orden descendente
        qemu_vms_list = sorted(qemu_vms_list, key=lambda vm: vm['vmid'], reverse=True)
        lxc_vms_list = sorted(lxc_vms_list, key=lambda vm: vm['vmid'], reverse=True)

        # Paginar los resultados
        paginator_qemu = Paginator(qemu_vms_list, 10)  # Muestra 10 VMs por página
        paginator_lxc = Paginator(lxc_vms_list, 10)  # Muestra 10 contenedores por página

        page_number_qemu = request.GET.get('page_qemu')
        page_number_lxc = request.GET.get('page_lxc')

        page_qemu = paginator_qemu.get_page(page_number_qemu)
        page_lxc = paginator_lxc.get_page(page_number_lxc)

        context = {
            'qemu_vms': page_qemu,
            'lxc_vms': page_lxc,
        }

        return render(request, 'proxmox_app/list_vms.html', context)
    except Exception as e:
        print(f"Error al obtener los nodos: {e}")
        return render(request, 'proxmox_app/list_vms.html', {'qemu_vms': [], 'lxc_vms': []})








def start_vm(request, vmid):
    try:
        proxmox.nodes('test').qemu(vmid).status.start.post()
        return redirect('list_vms')
    except Exception as e:
        print(f"Error al iniciar la VM {vmid}: {e}")
        return redirect('list_vms')


def stop_vm(request, vmid):
    try:
        proxmox.nodes('test').qemu(vmid).status.stop.post()
        return redirect('list_vms')
    except Exception as e:
        print(f"Error al detener la VM {vmid}: {e}")
        return redirect('list_vms')


def restart_vm(request, vmid):
    try:
        proxmox.nodes('test').qemu(vmid).status.reboot.post()
        return redirect('list_vms')
    except Exception as e:
        print(f"Error al reiniciar la VM {vmid}: {e}")
        return redirect('list_vms')


def start_container(request, vmid):
    try:
        proxmox.nodes('test').lxc(vmid).status.start.post()
        return redirect('list_vms')
    except Exception as e:
        print(f"Error al iniciar el contenedor {vmid}: {e}")
        return redirect('list_vms')


def stop_container(request, vmid):
    try:
        proxmox.nodes('test').lxc(vmid).status.stop.post()
        return redirect('list_vms')
    except Exception as e:
        print(f"Error al detener el contenedor {vmid}: {e}")
        return redirect('list_vms')


def restart_container(request, vmid):
    try:
        proxmox.nodes('test').lxc(vmid).status.reboot.post()
        return redirect('list_vms')
    except Exception as e:
        print(f"Error al reiniciar el contenedor {vmid}: {e}")
        return redirect('list_vms')


def create_snapshot(request):
    if request.method == "POST":
        snapshot_name = request.POST.get('snapshot_name', 'snapshot')
        include_ram = '1' if request.POST.get('include_ram', 'off') == 'on' else '0'  # Convertir a '1' o '0'
        description = request.POST.get('description', '')
        vm_ids = request.POST.getlist('vm_ids')  # Obtener lista de VM seleccionadas

        if not snapshot_name or not vm_ids:
            return redirect('list_vms')

        for vmid in vm_ids:
            try:
                # Crear snapshot para cada VM seleccionada con los parámetros correctos
                proxmox.nodes('test').qemu(vmid).snapshot.create(
                    snapname=snapshot_name,
                    description=description,
                    vmstate=include_ram  # Esto se convertirá en '1' o '0' en lugar de True/False
                )
                print(f"Snapshot creado exitosamente para VM {vmid}")
            except Exception as e:
                print(f"Error creando snapshot para VM {vmid}: {e}")

        return redirect('list_vms')

    return redirect('list_vms')

##################### Listar Snapshots ###########################

def list_snapshots(request, vmid):
    try:
        # Obtener las snapshots de la VM (qemu)
        snapshots = proxmox.nodes('test').qemu(vmid).snapshot.get()

        # Crear el contexto con la lista de snapshots y el ID de la VM
        context = {
            'vmid': vmid,
            'snapshots': snapshots,
        }

        # Renderizar la plantilla con los snapshots
        return render(request, '/opt/site/horeb/templates/proxmox_app/list_snapshots', context)

    except Exception as e:
        print(f"Error obteniendo snapshots para la VM {vmid}: {e}")
        # No redirigir a la lista de VMs en caso de error, mostrar un mensaje de error en la misma página
        return render(request, '/opt/site/horeb/templates/proxmox_app/list_snapshots', {
            'error_message': f"Error obteniendo snapshots para la VM {vmid}: {e}",
            'snapshots': [],
            'vmid': vmid
        })



################### Eliminar Snapshots #########################

def delete_snapshot(request, vmid, snapname):
    try:
        # Eliminar el snapshot específico de la VM
        proxmox.nodes('test').qemu(vmid).snapshot(snapname).delete()
        print(f"Snapshot {snapname} eliminado exitosamente para VM {vmid}")
    except Exception as e:
        print(f"Error eliminando snapshot {snapname} para VM {vmid}: {e}")

    # Redirigir al listado de snapshots después de la eliminación
    return redirect('list_snapshots', vmid=vmid)


################ CREAR VM #################################################################################################

def list_resources(request):
    try:
        # Obtener los nodos del cluster
        nodes = proxmox.nodes.get()

        # Diccionario para almacenar las redes y almacenamiento de cada nodo
        network_options = {}
        storage_options = {}

        # Recorremos los nodos para obtener sus redes y almacenamiento
        for node in nodes:
            node_name = node['node']

            # Obtener redes del nodo
            network_options[node_name] = get_networks(node_name)

            # Obtener almacenamiento del nodo
            storage_options[node_name] = get_storage_options(node_name)

        # Crear el contexto para la plantilla
        context = {
            'nodes': nodes,
            'network_options': network_options,
            'storage_options': storage_options,
        }

        # Renderizar la plantilla con los datos de redes, nodos y almacenamiento
        return render(request, '/opt/site/horeb/templates/proxmox_app/list_resources.html', context)

    except Exception as e:
        print(f"Error al obtener recursos de Proxmox: {e}")
        return render(request, '/opt/site/horeb/templates/proxmox_app/list_resources.html', {
            'error_message': f"Error al obtener recursos: {e}"
        })


# Función para obtener el próximo ID disponible de VM
def get_next_vm_id():
    try:
        vms = proxmox.cluster.resources.get(type='vm')
        # Obtener la lista de IDs en uso y encontrar el ID más alto
        used_ids = [int(vm['vmid']) for vm in vms]
        max_id = max(used_ids) if used_ids else 0
        
        # Evitar que el ID empiece por 100
        next_id = max_id + 1 if max_id >= 100 else 101
        return next_id
    except Exception as e:
        print(f"Error al obtener el siguiente ID de VM: {e}")
        return None

# Función para crear una VM en Proxmox

def create_vm(request):
    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            node = request.POST.get('node')
            vm_name = request.POST.get('vm_name')
            ram = request.POST.get('ram', '0')  # Valor predeterminado en caso de que esté vacío
            disk = request.POST.get('disk', '0')  # Valor predeterminado en caso de que esté vacío
            cpu = request.POST.get('cpu', '1')  # Valor predeterminado en caso de que esté vacío
            network = request.POST.get('network')
            storage_disk = request.POST.get('storage_disk')
            storage_iso = request.POST.get('storage_iso')
            iso_image = request.POST.get('iso_image')

            # Validación de los campos numéricos
            if not ram or not disk or not cpu:
                return render(request, '/opt/site/horeb/templates/proxmox_app/create_vm.html', {
                    'error_message': 'Por favor ingrese valores válidos para RAM, Disco y CPU.'
                })

            # Convertir los valores a enteros
            ram = int(ram) * 1024  # Convertir a MB
            disk = int(disk)
            cpu = int(cpu)

            # Obtener el próximo ID de VM
            vm_id = get_next_vm_id()

            if vm_id is None:
                return render(request, '/opt/site/horeb/templates/proxmox_app/create_vm.html', {
                    'error_message': 'Error al generar el ID de la VM'
                })

            # Crear la VM en Proxmox con parámetros correctos
            proxmox.nodes(node).qemu.create(
                vmid=vm_id,
                name=vm_name,
                memory=ram,  # RAM en MB
                cores=cpu,
                scsi0=f"{storage_disk}:{disk},iothread=1",  # Añadir iothread y ajustar el tamaño del disco desde el formulario
                scsihw="virtio-scsi-single",  # Especificar el controlador de disco
                net0=f"virtio=BC:24:11:3E:0E:A4,bridge={network},firewall=1",  # Añadir el firewall a la interfaz de red
                ostype='l26',
                boot='order=scsi0;ide2;net0',  # Orden de arranque
                ide2=f"{iso_image},media=cdrom",  # Usar la imagen ISO seleccionada desde el formulario
                cdrom=f"{iso_image}",  # Usar la imagen ISO
                cpu="x86-64-v2-AES"
                #scsi0=f"{storage_disk}:{disk}",  # Especificar correctamente el almacenamiento y tamaño del disco
                #net0=f"model=virtio,bridge={network}",
                #ostype='l26',  # Cambiar según sea necesario
                #boot='cdn',
                #ide2=f"{iso_image},media=cdrom",  # Usar la imagen ISO seleccionada
                #cdrom=f"{iso_image}"  # Usar la imagen ISO seleccionada
            )

            # Redirigir a una página de éxito o lista de VMs si la creación es exitosa
            return redirect('list_vms')  # Asegúrate de tener esta ruta configurada

        except Exception as e:
            print(f"Error al crear la VM: {e}")
            # Si ocurre una excepción, devolver el formulario con el mensaje de error
            return render(request, '/opt/site/horeb/templates/proxmox_app/create_vm.html', {
                'error_message': f"Error al crear la VM: {e}"
            })

    else:  # Si es un GET, mostrar el formulario
        try:
            nodes = proxmox.nodes.get()
            network_options = {}
            storage_options = {}
            iso_images = []

            # Obtener redes y almacenamiento para cada nodo
            for node in nodes:
                node_name = node['node']
                network_options[node_name] = get_networks(node_name)
                storage_options[node_name] = get_storage_options(node_name)

            # Verificar si ya se ha seleccionado un almacenamiento ISO para listar las imágenes
            if 'storage_iso' in request.GET:
                storage_iso = request.GET['storage_iso']
                iso_images = get_iso_images(node_name, storage_iso)  # Llamada para obtener las imágenes ISO

            # Renderizar el formulario para crear la VM
            context = {
                'nodes': nodes,
                'network_options': network_options,
                'storage_options': storage_options,
                'iso_images': iso_images  # Pasar las imágenes ISO al contexto
            }
            return render(request, '/opt/site/horeb/templates/proxmox_app/create_vm.html', context)

        except Exception as e:
            print(f"Error al obtener recursos para crear VM: {e}")
            return render(request, '/opt/site/horeb/templates/proxmox_app/create_vm.html', {
                'error_message': f"Error al obtener recursos: {e}"
            })





# Función para obtener redes disponibles en el nodo
# Función para obtener redes disponibles en el nodo
def get_networks(node_name):
    try:
        networks = proxmox.nodes(node_name).network.get()
        # Verificar que cada red tenga la clave 'iface' y opcionalmente 'bridge'
        bridge_networks = [{'iface': net['iface'], 'bridge': net.get('bridge', 'N/A')} for net in networks if 'iface' in net]
        return bridge_networks
    except Exception as e:
        print(f"Error obteniendo redes del nodo {node_name}: {e}")
        return []


# Función para obtener almacenamiento disponible en el nodo
def get_storage_options(node_name):
    try:
        storages = proxmox.nodes(node_name).storage.get()
        # Retornar solo el nombre del almacenamiento
        return [storage['storage'] for storage in storages if storage['enabled']]
    except Exception as e:
        print(f"Error obteniendo opciones de almacenamiento del nodo {node_name}: {e}")
        return []

# Función para obtener las imágenes ISO disponibles en un almacenamiento específico
def get_iso_images(node_name, storage_name):
    try:
        # Listar los contenidos del almacenamiento (por ejemplo, ISO)
        contents = proxmox.nodes(node_name).storage(storage_name).content.get()
        iso_images = [content['volid'] for content in contents if content['content'] == 'iso']
        return iso_images
    except Exception as e:
        print(f"Error obteniendo imágenes ISO del almacenamiento {storage_name} en el nodo {node_name}: {e}")
        return []
