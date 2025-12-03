"""
data_fetcher.py
Módulo que maneja la descarga (o uso de caché) de la serie de tiempo del World Bank
para el indicador SH.IMM.MEAS (Immunization, measles) para un país.
Si no hay conexión, usa un archivo de muestra incluido (sample_data.json).
"""

import requests, json, os, datetime

WORLD_BANK_API = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&per_page=1000"

# Sample minimal data included for offline use (Panama sample years).
sample_data = [
    {"country": "Panama", "countryiso3code": "PAN", "date": "2022", "value": 92.0},
    {"country": "Panama", "countryiso3code": "PAN", "date": "2021", "value": 92.0},
    {"country": "Panama", "countryiso3code": "PAN", "date": "2020", "value": 95.0},
    {"country": "Panama", "countryiso3code": "PAN", "date": "2019", "value": 97.0},
    {"country": "Panama", "countryiso3code": "PAN", "date": "2018", "value": 96.0}
]

class WorldBankCache:
    def __init__(self, country_code="PAN", indicator="SH.IMM.MEAS", cache_file="data/cache.json"):
        self.country = country_code
        self.indicator = indicator
        self.cache_file = cache_file
        self._data = None

    def source_info(self):
        return {"provider": "World Bank (API)", "indicator": self.indicator, "country": self.country}

    def ensure_data(self):
        # Try load from cache file first
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                    return
            except Exception:
                pass
        # Try to fetch from World Bank API
        try:
            url = WORLD_BANK_API.format(country=self.country, indicator=self.indicator)
            resp = requests.get(url, timeout=8)
            resp.raise_for_status()
            payload = resp.json()
            # payload[1] contains series entries when success
            entries = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
            # Map to simpler records
            records = []
            for e in entries:
                records.append({
                    "country": e.get("country", {}).get("value"),
                    "countryiso3code": e.get("countryiso3code"),
                    "year": e.get("date"),
                    "value": e.get("value")
                })
            # Sort by year ascending
            records = sorted(records, key=lambda r: int(r["year"]))
            os.makedirs(os.path.dirname(self.cache_file) or ".", exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            self._data = records
        except Exception:
            # Fallback to bundled sample data
            self._data = sample_data

    def get_all(self):
        if self._data is None:
            self.ensure_data()
        return self._data or []

    def get_by_year(self, year: int):
        if self._data is None:
            self.ensure_data()
        for rec in self._data:
            try:
                if int(rec.get("year")) == int(year):
                    return rec
            except Exception:
                continue
        return None

    def get_latest(self):
        if self._data is None:
            self.ensure_data()
        if not self._data:
            return None
        # assume sorted ascending
        return self._data[-1]
