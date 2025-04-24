
from datetime import datetime
from models.tables import Forecast, Hour


class SavePredictions:

    def save_predictions(self, pred_df, info_adicional, city, db):
        forecast_day_list = []
        unique_dates = sorted(pred_df['datetime'].dt.date.unique())

        for fecha in unique_dates:
            grupo = pred_df[pred_df['datetime'].dt.date == fecha]
            hour_forecast = []
            for _, row in grupo.iterrows():
                registro_hora = {
                    "date_time": row["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                    "temp_c": row["temp_pred"],
                    "humidity": row["humidity_pred"]
                }
                hour_forecast.append(registro_hora)

            info_match = next((item for item in info_adicional if item.get("date") == fecha.strftime("%Y-%m-%d")), None)
            if info_match is None:
                info_match = info_adicional[-1] if info_adicional else {}

            forecast_entry = {
                "date": fecha.strftime("%Y-%m-%d"),
                "astro": info_match.get("astro", {}),
                "hour": hour_forecast
            }
            forecast_day_list.append(forecast_entry)

        output_api_structure = {
            "location": info_adicional[0].get("location", {}) if info_adicional else {},
            "forecast": {
                "forecastday": forecast_day_list
            }
        }

        # 7. Guardar en base de datos
        inserted_forecasts = []
        for block in forecast_day_list:
            forecast_obj = Forecast(
                city=city,
                forecast_date=datetime.strptime(block["date"], "%Y-%m-%d").date(),
                astro=block["astro"],
                location=output_api_structure["location"]
            )
            db.add(forecast_obj)
            db.commit()
            db.refresh(forecast_obj)
            inserted_forecasts.append(forecast_obj)

            for hr in block["hour"]:
                hour_obj = Hour(
                    forecast_id=forecast_obj.id,
                    date_time=datetime.strptime(hr["date_time"], "%Y-%m-%d %H:%M:%S"),
                    temp_pred=hr["temp_c"],
                    humidity_pred=hr["humidity"]
                )
                db.add(hour_obj)
            db.commit()

        return inserted_forecasts, info_adicional