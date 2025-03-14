

from models.tables import Predictions

class SavePredictions:
    def save_info(self, data, prediction, date_future, data_api, db):
        data_predictions = Predictions(
            city=data[0][19],
            region=data[0][20],
            country=data[0][21],
            lat=data[0][0],
            lon=data[0][1],
            temp_c=float(prediction.iloc[0]["temp_c"]),
            localtime=data[0][22],
            localtime_future=date_future,
            wind_mph=data[0][2],
            wind_degree=data[0][3],
            pressure_mb=data[0][4],
            precip_mm=data[0][5],
            humidity=float(prediction.iloc[0]["humidity"]),
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
            us_epa_index=data[0][17],
            gb_defra_index=data[0][18],
            input_id=data_api.id,)
        db.add(data_predictions)
        db.commit()
        db.refresh(data_predictions)
        print(float(prediction.iloc[0]["humidity"]))
        return data_predictions