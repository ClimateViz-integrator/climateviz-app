import numpy as np
import pandas as pd
from models.tables import Input_data

class DataToSave:
    def prepare_input_data(self, data, db):
        """Prepara y guarda datos de entrada en la base de datos."""

        city_data_list = []
        data_api_list = []
        ids = []

        for row in data:
            # Convertir a lista si es un array de NumPy
            row = row.tolist() if isinstance(row, np.ndarray) else row
            
            data_api = Input_data(
                lat=row[0], lon=row[1], wind_kph=row[2], wind_degree=row[3],
                pressure_mb=row[4], precip_mm=row[5], cloud=row[6], 
                feelslike_c=row[7], vis_km=row[8], uv=row[9]
            )
            
            db.add(data_api)
            db.commit()
            ids.append(data_api.id)
            db.refresh(data_api)
              # Guardar el ID del registro creado

            # Guardar en listas para retornarlas después
            data_api_list.append(data_api)
            city_data_list.append(row[:11])  # Solo las primeras 10 columnas relevantes
        return np.array(city_data_list), ids

          

    def create_dataframe_from_array(self, city_data):
        """Convierte un array de datos en un DataFrame con las columnas correctas"""
        columns = [
            "lat",
            "lon",
            "wind_kph",
            "wind_degree",
            "pressure_mb",
            "precip_mm",
            "cloud",
            "feelslike_c",
            "vis_km",
            "uv",
            "humidity",
        ]
        return pd.DataFrame(city_data, columns=columns)