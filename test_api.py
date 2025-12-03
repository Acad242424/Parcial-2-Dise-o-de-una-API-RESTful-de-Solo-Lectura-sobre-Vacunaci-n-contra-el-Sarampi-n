import pytest
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

def test_get_all():
    r = client.get("/vacunas")
    assert r.status_code == 200
    j = r.json()
    assert "data" in j
    assert isinstance(j["data"], list)

def test_get_year_existing_or_404():
    # pick a year from the sample data
    sample_year = 2022
    r = client.get(f"/vacunas/{sample_year}")
    if r.status_code == 200:
        j = r.json()
        assert j["data"]["year"] == str(sample_year) or j["data"]["year"] == sample_year
    else:
        assert r.status_code == 404

def test_provincia_simulated():
    r = client.get("/vacunas/provincia/Panamá")
    assert r.status_code == 200
    j = r.json()
    assert "data" in j and "province" in j["data"]
