
from models.tables import Predictions
import pandas as pd
from fastapi.responses import FileResponse
import tempfile
from pathlib import Path

class ReportController:

    def export_data_excel(self, db):
        """
        Exporta los datos a un archivo Excel y lo devuelve para su descarga.
        """
        predictions = db.query(Predictions).all()
        data = [[
            pred.city, pred.region, pred.country, pred.lat, pred.lon, pred.temp_c, 
            pred.localtime, pred.localtime_future, pred.wind_mph, pred.wind_degree, 
            pred.pressure_mb, pred.precip_mm, pred.humidity, pred.cloud, pred.feelslike_c, 
            pred.vis_km, pred.uv, pred.co, pred.o3, pred.no2, pred.so2, pred.pm2_5, 
            pred.pm10, pred.us_epa_index, pred.gb_defra_index
        ] for pred in predictions]

        df = pd.DataFrame(data, columns=[
            "city", "region", "country", "lat", "lon", "temp_c", "localtime", "localtime_future", 
            "wind_mph", "wind_degree", "pressure_mb", "precip_mm", "humidity", "cloud", 
            "feelslike_c", "vis_km", "uv", "co", "o3", "no2", "so2", "pm2_5", "pm10", 
            "us_epa_index", "gb_defra_index"
        ])

        # Crear un archivo temporal en formato Excel
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            temp_file_path = Path(tmp_file.name)
            df.to_excel(temp_file_path, index=False, engine='openpyxl')

        # Retornar el archivo para descarga
        return FileResponse(path=temp_file_path, filename="reporte.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")