# 📘 Changelog

Este documento registra los cambios realizados en el proyecto **Automatizaciones de Pauta Digital en Fusion Agency**.

Todos los cambios significativos seguirán el formato [Keep a Changelog](https://keepachangelog.com/es/1.0.0/) y versionado semántico.

---

## [v1.0.0] - 2025-04-29

### Agregado
- Scripts `meta_gastos_mes.py` para automatizar gastos diarios desde Meta Ads a Google Sheets.
- Programación automática diaria vía `cron` a las 07:30 AM.
- Archivos `.env` y `credenciales/` estructurados correctamente con rutas portables.
- Carga y limpieza de datos desde archivos Excel y CSV.
- Scripts: `db-reviews.py`, `db-sevenrooms.py`, `db-partition.py` unificados bajo buenas prácticas.
- Archivo `requirements.txt` con dependencias claras.
- Documentación inicial con `README.md`.

## [2.0.0] - 2025-07-31
### Añadido
- `.env` para configuración y credenciales.
- Scripts `FCG_consumo.py`, `V&V_consumo.py`, `VYVE_consumo.py` para automatizar gastos diarios desde Meta Ads a Google Sheets.
- Script `extender_token_ads.py` y generación dinámica de token Meta Ads.
- Script `run_all.sh` con logs, errores y orquestación secuencial.
- Carpeta `data`, `dataReviews`, `processedData` para estructuración de datos.
- Documentación técnica (`wrapperScript-implementation.md`, `automatizaciones-alias.md`).

### Cambiado
- Migración de rutas y credenciales fuera del código.
- Integración más robusta con `cron`.

### Eliminado
- Configuraciones embebidas en código.

## [2.1.0] - 2025-08-01
### Añadido
- Funcionalidad para hacer partición de "Otros" en el archivo `db_partition.py`, para que se distribuya al canal de *PAUTA* y *MAILING*.
- Nuevos requirements

### Cambiado
- Ajustes menores en `db_partition.py` para soportar la nueva lógica.

