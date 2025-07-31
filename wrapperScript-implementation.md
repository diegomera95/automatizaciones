# Guía: Implementación de un Wrapper Script para Automatizaciones en Bash

## Ventajas:

* Centralizar la ejecución de múltiples scripts automáticos mediante un solo script (wrapper), programado desde `crontab`.
* Mantenimiento simplificado (una sola entrada en `crontab`)
* Control secuencial de ejecuciones con pausas
* Logs separados por script o unificados
* Fácil de escalar a más scripts

# Estructura del Script (ejemplo base)

    #!/bin/bash

    PYTHON_PATH="/home/pautadigital/.pyenv/versions/3.10.13/envs/automatizaciones/bin/python3"
        ## "/ruta/a/python3"
    SCRIPTS_DIR="/home/pautadigital/Projects/dotfiles/Automatizaciones"  
        ## "/ruta/a/scripts"
    LOG_DIR="/home/pautadigital/cron_logs"
        ## "/ruta/a/logs"

    # Lista de scripts a ejecutar
    SCRIPTS=("V&V_consumo.py" "VYVE_consumo.py" "FCG_consumo.py")
        ## ("script1.py" "script2.py" "script3.py")

    for SCRIPT in "${SCRIPTS[@]}"; do
        echo "Ejecutando $SCRIPT..."
        "$PYTHON_PATH" "$SCRIPTS_DIR/$SCRIPT" >> "$LOG_DIR/${SCRIPT%.py}.log" 2>&1
        echo "$SCRIPT finalizado. Esperando 15 segundos..."
        sleep 15
    done

## Pasos para Implementarlo

### Crear el archivo del script:
Guarda el contenido anterior como `run_all.sh`.

### Dar permisos de ejecución:

`chmod +x /home/pautadigital/Projects/dotfiles/Automatizaciones/run_all.sh`
    ##chmod +x /ruta/a/run_all.sh

### Programar con crontab: Abre el editor de crontab:

`crontab -e` "" si es que te redirije a code ejecutar el siguiente `EDITOR=nano crontab -e`

### Agrega la línea:

`30 9 * * * /home/pautadigital/Projects/dotfiles/Automatizaciones/run_all.sh` 
    ## 30 9 * * * /ruta/a/run_all.sh

Esto ejecutará el wrapper todos los días a las 9:30 AM.

## Manejo de errores:

if [ $? -ne 0 ]; then
    echo "Error en $SCRIPT" >> "$LOG_DIR/errores.log"
fi

## Verificación de existencia del script:

if [ -f "$SCRIPTS_DIR/$SCRIPT" ]; then
    # Ejecutar
fi