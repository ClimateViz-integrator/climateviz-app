from models.tables import Predictions
from collections import OrderedDict

class SavePredictions:
    def save_info(self, data, predictions, date_futures, ids, db):
        results = []
    
        for i in range(len(predictions)):  
            if i < len(ids):  # Verificar que tenemos un id correspondiente
                data_predictions = Predictions(
                    city=data[0][19],
                    region=data[0][20],
                    country=data[0][21],
                    lat=data[0][0],
                    lon=data[0][1],
                    temp_c=float(predictions.iloc[i]["temp_c"]),
                    localtime=data[0][22],
                    localtime_future=date_futures[i],
                    wind_mph=data[0][2],
                    wind_degree=data[0][3],
                    pressure_mb=data[0][4],
                    precip_mm=data[0][5],
                    humidity=float(predictions.iloc[i]["humidity"]),
                    cloud=data[0][6],
                    feelslike_c=data[0][7],
                    vis_km=data[0][8],
                    uv=data[0][9],
                    co=data[0][11],
                    o3=data[0][12],
                    no2=data[0][13],
                    so2=data[0][14],
                    pm2_5=data[0][15],
                    pm10=data[0][16],
                    us_epa_index=data[0][17],
                    gb_defra_index=data[0][18],
                    # Asignamos el id correspondiente a esta predicción
                    input_id=ids[i]
                )
                db.add(data_predictions)
                db.commit()
                db.refresh(data_predictions)

                ordered_data = OrderedDict([
                    ("city", data_predictions.city),
                    ("region", data_predictions.region),
                    ("country", data_predictions.country),
                    ("lat", data_predictions.lat),
                    ("lon", data_predictions.lon),
                    ("temp_c", data_predictions.temp_c),
                    ("localtime", data_predictions.localtime),
                    ("localtime_future", data_predictions.localtime_future),
                    ("wind_mph", data_predictions.wind_mph),
                    ("wind_degree", data_predictions.wind_degree),
                    ("pressure_mb", data_predictions.pressure_mb),
                    ("precip_mm", data_predictions.precip_mm),
                    ("humidity", data_predictions.humidity),
                    ("cloud", data_predictions.cloud),
                    ("feelslike_c", data_predictions.feelslike_c),
                    ("vis_km", data_predictions.vis_km),
                    ("uv", data_predictions.uv),
                    ("co", data_predictions.co),
                    ("o3", data_predictions.o3),
                    ("no2", data_predictions.no2),
                    ("so2", data_predictions.so2),
                    ("pm2_5", data_predictions.pm2_5),
                    ("pm10", data_predictions.pm10),
                    ("us_epa_index", data_predictions.us_epa_index),
                    ("gb_defra_index", data_predictions.gb_defra_index),
                    ("input_id", data_predictions.input_id),
                ])
                results.append(ordered_data)

        return results
