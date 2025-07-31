#!/bin/bash

# Cargar variables desde el archivo .env
if [ -f "$(dirname "$0")/.env" ]; then
    source "$(dirname "$0")/.env"
else
    echo "No se encontró el archivo .env. Saliendo..."
    exit 1
fi

# Lista de scripts a ejecutar
SCRIPTS=("V&V_consumo.py" "VYVE_consumo.py" "FCG_consumo.py")
    ## ("script1.py" "script2.py" "script3.py")

for SCRIPT in "${SCRIPTS[@]}"; do
    FECHA=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$FECHA] Ejecutando $SCRIPT..." | tee -a "$LOG_DIR/${SCRIPT%.py}.log" "$LOG_DIR/ejecuciones.log"

    if [ -f "$SCRIPTS_DIR/$SCRIPT" ]; then
        "$PYTHON_PATH" "$SCRIPTS_DIR/$SCRIPT" >> "$LOG_DIR/${SCRIPT%.py}.log" 2>&1
        if [ $? -ne 0 ]; then
            echo "[$FECHA] Error al ejecutar $SCRIPT" >> "$LOG_DIR/errores.log"
        else
            echo "[$FECHA] Finalizado $SCRIPT. Esperando 10 segundos..." | tee -a "$LOG_DIR/${SCRIPT%.py}.log" "$LOG_DIR/ejecuciones.log"
        fi
    else
        echo "[$FECHA] Script no encontrado: $SCRIPT" >> "$LOG_DIR/errores.log"
    fi

    sleep 10
done