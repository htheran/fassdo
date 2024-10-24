from proxmoxer import ProxmoxAPI
from settings.models import Setting, SSHKey

# Función para obtener credenciales dinámicas
def get_proxmox_connection():
    try:
        # Obtener el usuario de Proxmox
        proxmox_user = Setting.objects.get(key='proxmox_user').value

        # Verificar si la contraseña está almacenada
        proxmox_password_setting = Setting.objects.filter(key='proxmox_password').first()
        proxmox_password = proxmox_password_setting.value if proxmox_password_setting else None

        # Verificar si se tiene una llave SSH
        ssh_keys = SSHKey.objects.first()

        if proxmox_password:
            # Conectar usando contraseña
            return ProxmoxAPI('10.100.0.5', user=proxmox_user, password=proxmox_password, verify_ssl=False)
        elif ssh_keys and ssh_keys.private_key:
            # Conectar usando llave SSH
            private_key_path = ssh_keys.private_key.path
            return ProxmoxAPI('10.100.0.5', user=proxmox_user, privkey=private_key_path, verify_ssl=False)
        else:
            raise Exception("No se encontró un método de autenticación válido (contraseña o llave SSH)")
    except Exception as e:
        raise Exception(f"Error al establecer la conexión con Proxmox: {e}")
