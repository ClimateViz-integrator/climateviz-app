from datetime import datetime
from models.tables import Forecast, Hour


class SavePredictions:

    def save_predictions(self, pred_df, info_adicional, city, db):
        forecast_day_list = []
        unique_dates = sorted(pred_df['datetime'].dt.date.unique())

        for fecha in unique_dates:
            grupo = pred_df[pred_df['datetime'].dt.date == fecha]
            hour_forecast = []
            
            # Buscar la información adicional para esta fecha
            info_match = next((item for item in info_adicional if item.get("date") == fecha.strftime("%Y-%m-%d")), None)
            if info_match is None:
                info_match = info_adicional[-1] if info_adicional else {}
            
            # Obtener los datos horarios de la información adicional
            hourly_data_additional = {}
            if "hourly_data" in info_match:
                for hour_info in info_match["hourly_data"]:
                    hour_time = datetime.strptime(hour_info["time"], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M:%S")
                    hourly_data_additional[hour_time] = hour_info
            
            # Procesar cada hora del grupo
            for _, row in grupo.iterrows():
                datetime_str = row["datetime"].strftime("%Y-%m-%d %H:%M:%S")
                
                # Obtener datos adicionales si están disponibles
                additional_hour_data = hourly_data_additional.get(datetime_str, {})
                
                registro_hora = {
                    "date_time": datetime_str,
                    "temp_c": row.get("temp_pred", None),
                    "humidity": row.get("humidity_pred", None),
                    "wind_kph": row.get("wind_kph", additional_hour_data.get("wind_kph", None)),
                    "cloud": row.get("cloud", additional_hour_data.get("cloud", None)),
                    "uv": row.get("uv", additional_hour_data.get("uv", None)),
                    # Añadir más campos si están disponibles en row o additional_hour_data
                    # "wind_degree": row.get("wind_degree", additional_hour_data.get("wind_degree", None)),
                    # "wind_dir": additional_hour_data.get("wind_dir", None),
                    # "precip_mm": additional_hour_data.get("precip_mm", None),
                    # "gust_kph": additional_hour_data.get("gust_kph", None),
                    # "is_day": additional_hour_data.get("is_day", None),
                    # "vis_km": additional_hour_data.get("vis_km", None),
                    # "feelslike_c": additional_hour_data.get("feelslike_c", None),
                    # "chance_of_rain": additional_hour_data.get("chance_of_rain", None),
                    # "condition": additional_hour_data.get("condition", None)
                }
                hour_forecast.append(registro_hora)

            forecast_entry = {
                "date": fecha.strftime("%Y-%m-%d"),
                "astro": info_match.get("astro", {}),
                "day": info_match.get("forecast_day", {}),  # Añadir información del día
                "hour": hour_forecast,
            }
            forecast_day_list.append(forecast_entry)

        output_api_structure = {
            "location": info_adicional[0].get("location", {}) if info_adicional else {},
            "current": info_adicional[0].get("current", {}) if info_adicional else {},  # Añadir datos actuales
            "forecast": {
                "forecastday": forecast_day_list
            },
            "alerts": info_adicional[0].get("alerts", []) if info_adicional else []  # Añadir alertas
        }

        # 7. Guardar en base de datos
        inserted_forecasts = []
        for block in forecast_day_list:
            forecast_obj = Forecast(
                city=city,
                forecast_date=datetime.strptime(block["date"], "%Y-%m-%d").date(),
                astro=block["astro"],
                day=block.get("day", {}),  # Guardar información del día
                location=output_api_structure["location"]
            )
            db.add(forecast_obj)
            db.commit()
            db.refresh(forecast_obj)
            inserted_forecasts.append(forecast_obj)

            for hr in block["hour"]:
                # Crear un diccionario con todos los campos disponibles
                hour_data = {
                    "forecast_id": forecast_obj.id,
                    "date_time": datetime.strptime(hr["date_time"], "%Y-%m-%d %H:%M:%S"),
                    "temp_pred": hr.get("temp_c"),
                    "humidity_pred": hr.get("humidity")
                }
                
                # Añadir campos adicionales si existen en la tabla Hour
                additional_fields = [
                    "wind_kph", "cloud", "uv"
                ]
                
                for field in additional_fields:
                    if hr.get(field) is not None:
                        hour_data[field] = hr[field]
                
                # Crear objeto Hour con los campos relevantes
                hour_obj = Hour(**hour_data)
                db.add(hour_obj)
            
            db.commit()

        return inserted_forecasts, output_api_structure