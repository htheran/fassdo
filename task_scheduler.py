import time
import subprocess
import datetime

# Definir la ruta del archivo de log
log_file_path = '/opt/site/horeb/logs/task_scheduler.log'

def escribir_log(mensaje):
    """Escribe un mensaje en el archivo de log con la fecha y hora."""
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{datetime.datetime.now()}: {mensaje}\n")

def ejecutar_tarea():
    """Ejecuta la tarea y registra la salida y los errores."""
    try:
        # Ejecutar el comando y capturar la salida
        result = subprocess.run(
            ['/opt/site/venv/bin/python', '/opt/site/horeb/manage.py', 'execute_tasks'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,  # Captura también la salida de error
            text=True
        )
        # Registrar la salida estándar
        escribir_log(f"Salida estándar: {result.stdout}")
        
        # Registrar la salida de error, si existe
        if result.stderr:
            escribir_log(f"Error: {result.stderr}")
            
    except Exception as e:
        # Registrar cualquier excepción en el log
        escribir_log(f"Excepción durante la ejecución: {str(e)}")

while True:
    escribir_log("Ejecutando tarea programada.")
    ejecutar_tarea()
    time.sleep(60)  # Espera 60 segundos antes de ejecutar nuevamente

