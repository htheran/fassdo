#!/bin/bash

# Ruta de la llave privada
SSH_KEY="/opt/site/horeb/media/ssh_keys/id_rsa"

# Obtener el usuario y host remoto de los argumentos
REMOTE_USER=$1
REMOTE_HOST=$2

# Verificar que se haya pasado el argumento del usuario y host
if [[ -z "$REMOTE_USER" || -z "$REMOTE_HOST" ]]; then
    echo "Error: No se ha proporcionado el usuario o el host remoto."
    exit 1
fi

# Conexión SSH
ssh -i "$SSH_KEY" "$REMOTE_USER@$REMOTE_HOST" \
    -o StrictHostKeyChecking=no <<EOF
    echo "Conexión establecida correctamente con el host: $REMOTE_HOST"
EOF

if [[ $? -eq 0 ]]; then
    echo "Todo fue bien. Conexión exitosa."
else
    echo "Hubo un error al intentar conectar."
fi

