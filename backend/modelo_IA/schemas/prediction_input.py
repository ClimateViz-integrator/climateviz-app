from pydantic import BaseModel

class PredictionInput(BaseModel):
    lat: float
    lon: float
    wind_kph: float
    wind_degree: float
    pressure_mb: float
    precip_mm: float
    humidity: float
    cloud: float
    feelslike_c: float
    vis_km: float
    uv: float
    co: float
    o3: float
    no2: float
    so2: float
    pm2_5: float
    pm10: float
    us_epa_index: float
    gb_defra_index: float