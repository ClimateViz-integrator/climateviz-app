import numpy as np
import pandas as pd
from models.tables import Input_data

class DataToSave:
    def prepare_input_data(self, data, db):
        """Método auxiliar para preparar y guardar datos de entrada"""
        data_api = Input_data(
            lat=data[0][0],
            lon=data[0][1],
            wind_kph=data[0][2],
            wind_degree=data[0][3],
            pressure_mb=data[0][4],
            precip_mm=data[0][5],
            humidity=data[0][6],
            cloud=data[0][7],
            feelslike_c=data[0][8],
            vis_km=data[0][9],
            uv=data[0][10],
            co=data[0][11],
            o3=data[0][12],
            no2=data[0][13],
            so2=data[0][14],
            pm2_5=data[0][15],
            pm10=data[0][16],
            us_epa_index=int(data[0][17]) if data[0][17] is not None else None,
            gb_defra_index=int(data[0][18]) if data[0][18] is not None else None,
        )
        db.add(data_api)
        db.commit()
        db.refresh(data_api)

        # Crear array con los datos para la predicción
        city_data = np.array([[data[0][i] for i in range(17)]])
        return data_api, city_data

    def create_dataframe_from_array(self, city_data):
        """Convierte un array de datos en un DataFrame con las columnas correctas"""
        columns = [
            "lat",
            "lon",
            "wind_kph",
            "wind_degree",
            "pressure_mb",
            "precip_mm",
            "humidity",
            "cloud",
            "feelslike_c",
            "vis_km",
            "uv",
            "co",
            "o3",
            "no2",
            "so2",
            "pm2_5",
            "pm10",
        ]
        return pd.DataFrame(city_data, columns=columns)