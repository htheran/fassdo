from proxmoxer import ProxmoxAPI
from settings.models import Setting, SSHKey

# Función para obtener credenciales dinámicas
def get_proxmox_connection():
    try:
        # Obtener los datos de la base de datos
        proxmox_ip = Setting.objects.get(name='proxmox_ip').value
        proxmox_port = Setting.objects.get(name='proxmox_port').value
        proxmox_user = Setting.objects.get(name='proxmox_user').value
        proxmox_password = Setting.objects.filter(name='proxmox_password').first()

        ssh_keys = SSHKey.objects.first()

        # Validar que el IP no contenga 'https://'
        if proxmox_ip.startswith('https://'):
            proxmox_ip = proxmox_ip.split('https://')[1]  # Eliminar el esquema https si está presente

        # Construir la URL correctamente
        proxmox_url = f"{proxmox_ip}:{proxmox_port}"
        print(f"Connecting to Proxmox at: {proxmox_url}")

        # Conexión usando contraseña o llave SSH
        if proxmox_password:
            return ProxmoxAPI(proxmox_url, user=f"{proxmox_user}@pam", password=proxmox_password.value, verify_ssl=False)
        elif ssh_keys and ssh_keys.private_key:
            private_key_path = ssh_keys.private_key.path
            return ProxmoxAPI(proxmox_url, user=f"{proxmox_user}@pam", privkey=private_key_path, verify_ssl=False)
        else:
            raise Exception("No se encontró un método de autenticación válido (contraseña o llave SSH)")
    except Exception as e:
        raise Exception(f"Error al establecer la conexión con Proxmox: {e}")
