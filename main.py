from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from data_fetcher import WorldBankCache, sample_data
from typing import Dict, Any
import uvicorn

app = FastAPI(title="Vacunas API (Panamá) - Read-only",
              description="API GET-only para cobertura de vacunación contra el sarampión (12-23 meses) en Panamá. Fuente: World Bank (SH.IMM.MEAS)",
              version="1.0.0")

cache = WorldBankCache(country_code="PAN", indicator="SH.IMM.MEAS", cache_file="data/cache.json")

@app.on_event("startup")
def startup_event():
    # Try to load cached data; if not present, attempt to fetch from World Bank API.
    cache.ensure_data()

@app.get("/vacunas", response_class=JSONResponse)
def get_all():
    data = cache.get_all()
    return {"source": cache.source_info(), "count": len(data), "data": data}

@app.get("/vacunas/{year}", response_class=JSONResponse)
def get_by_year(year: int):
    record = cache.get_by_year(year)
    if not record:
        raise HTTPException(status_code=404, detail=f"No se encontró dato para el año {year}.")
    return {"source": cache.source_info(), "data": record}

@app.get("/vacunas/provincia/{provincia}", response_class=JSONResponse)
def get_by_province(provincia: str, year: int = None):
    """
    Datos por provincia/region. World Bank no ofrece datos subnacionales en SH.IMM.MEAS,
    por lo que este endpoint simula valores por provincia basados en el valor nacional.
    Optional query parameter 'year' filters the simulation to a specific year.
    """
    if year is None:
        # use latest available year
        record = cache.get_latest()
    else:
        record = cache.get_by_year(year)
    if not record:
        raise HTTPException(status_code=404, detail="Año no encontrado para la simulación.")
    national_value = record.get("value")
    if national_value is None:
        raise HTTPException(status_code=404, detail="No hay valor nacional para el año solicitado.")
    # Simulate provinces: distribute +/- up to 6% variation across sample provinces.
    provinces = ["Panamá", "Colón", "Chiriquí", "Coclé", "Veraguas", "Bocas del Toro", "Los Santos", "Herrera"]
    base = float(national_value)
    simulated = []
    import math, random
    random.seed(year or int(record.get("year", 0)))  # reproducible per year
    for p in provinces:
        # variation between -6% and +6%
        var = (random.random() - 0.5) * 0.12
        val = max(0.0, min(100.0, base * (1 + var)))
        simulated.append({"province": p, "year": int(record["year"]), "value": round(val, 1)})
    # Find requested province (case-insensitive)
    prov = provincia.strip().lower()
    for item in simulated:
        if item["province"].lower() == prov:
            return {"source": cache.source_info(), "data": item}
    raise HTTPException(status_code=404, detail=f"Provincia '{provincia}' no encontrada en la simulación.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
