# Vacunas API (Panamá) - Read-only

API RESTful (GET-only) para consultar cobertura de vacunación contra el sarampión en niños de 12-23 meses en Panamá.
Datos: World Bank indicator `SH.IMM.MEAS`.

## Endpoints
- `GET /vacunas` — Devuelve todos los registros disponibles.
- `GET /vacunas/{year}` — Devuelve datos para el año especificado.
- `GET /vacunas/provincia/{nombre}?year=YYYY` — Simula datos subnacionales por provincia (World Bank no provee datos regionales para este indicador).

## Ejecución (local)
1. Crear y activar un entorno virtual (recomendado).
2. Instalar dependencias:
```
pip install -r requirements.txt
```
3. Ejecutar la API:
```
uvicorn main:app --reload
```
4. Abrir `http://127.0.0.1:8000/docs` para ver la documentación automática de OpenAPI/Swagger.

## Notas
- La primera vez la API intentará descargar la serie completa desde la API pública del World Bank. Si fallara la descarga, usará un dataset de ejemplo incluido.
- El endpoint de provincia devuelve valores simulados (reproducibles por año) basados en el valor nacional.

## Tests
Ejecutar tests con:
```
pytest -q
```
