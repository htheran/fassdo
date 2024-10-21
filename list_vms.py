from proxmoxer import ProxmoxAPI
import json

# Configuración de conexión
#proxmox = ProxmoxAPI('10.100.0.5', user='root@pam', token_name='mate', token_value='9f82eaeb-504d-48f4-a788-619de2f561c8', verify_ssl=False)
proxmox = ProxmoxAPI('10.100.0.5', user='root@pam', password='Pr0l1ant', verify_ssl=False)
# Obtener la lista de nodos
try:
    nodes = proxmox.nodes.get()

    for node in nodes:
        print(f"Nodo: {node['node']}")
        
        # Intentar obtener las VMs QEMU
        try:
            vms_qemu = proxmox.nodes(node['node']).qemu.get()
            print(f"Respuesta cruda de las VMs QEMU para el nodo {node['node']}: {json.dumps(vms_qemu, indent=4)}")

            if vms_qemu:
                for vm in vms_qemu:
                    print(f"VM QEMU ID: {vm['vmid']}, Nombre: {vm.get('name', 'NoName')}, Estado: {vm.get('status', 'Desconocido')}")
            else:
                print("No se encontraron máquinas virtuales (QEMU) en este nodo.")
        except Exception as vm_error:
            print(f"Error al obtener las VMs QEMU del nodo {node['node']}: {vm_error}")

        # Intentar obtener contenedores LXC
        try:
            vms_lxc = proxmox.nodes(node['node']).lxc.get()
            print(f"Respuesta cruda de los contenedores LXC para el nodo {node['node']}: {json.dumps(vms_lxc, indent=4)}")

            if vms_lxc:
                for vm in vms_lxc:
                    print(f"Contenedor LXC ID: {vm['vmid']}, Nombre: {vm.get('name', 'NoName')}, Estado: {vm.get('status', 'Desconocido')}")
            else:
                print("No se encontraron contenedores LXC en este nodo.")
        except Exception as lxc_error:
            print(f"Error al obtener los contenedores LXC del nodo {node['node']}: {lxc_error}")

except Exception as e:
    print(f"Error al obtener los nodos: {e}")

