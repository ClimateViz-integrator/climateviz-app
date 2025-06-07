from fastapi import HTTPException
from fastapi.responses import FileResponse
from models.tables import Hour as Predictions, Forecast, PredictionsUser
from sqlalchemy.orm import Session
import pandas as pd
import tempfile
from pathlib import Path
from datetime import datetime

class ReportController:

    def export_data_excel(self, db: Session, user_id: int):
        try:
            # Validar si el usuario está autenticado
            if user_id is None:
                raise HTTPException(
                    status_code=401,
                    detail="Debe estar autenticado para generar el reporte. Por favor, inicie sesión o regístrese. 🔐"
                )

            # Obtener todos los hour_id asociados al user_id desde la tabla intermedia
            hour_ids = db.query(PredictionsUser.hour_id).filter(PredictionsUser.user_id == user_id).subquery()

            # Consultar las predicciones correspondientes a esas hour_ids
            predictions_with_forecast = (
                db.query(Predictions)
                .join(Forecast)
                .filter(Predictions.id.in_(hour_ids))
                .all()
            )

            # Validar si hay registros
            if not predictions_with_forecast:
                raise HTTPException(
                    status_code=404,
                    detail="No tienes registros de predicciones guardadas. Intenta generar una predicción primero. 🌤️"
                )

            # Construcción del reporte
            extended_data = []
            for pred in predictions_with_forecast:
                forecast = pred.forecast
                location = forecast.location or {}
                lat = location.get('lat', 'N/A')
                lon = location.get('lon', 'N/A')
                region = location.get('region', 'N/A')
                country = location.get('country', 'N/A')
                astro = forecast.astro or {}
                sunrise = astro.get('sunrise', 'N/A')
                sunset = astro.get('sunset', 'N/A')
                moon_phase = astro.get('moon_phase', 'N/A')

                extended_data.append([
                    pred.date_time,
                    forecast.city,
                    lat,
                    lon,
                    region,
                    country,
                    pred.temp_pred,
                    pred.humidity_pred,
                    pred.wind_kph,
                    pred.cloud,
                    pred.uv,
                    sunrise,
                    sunset,
                    moon_phase,
                ])

            # Crear DataFrame
            df = pd.DataFrame(extended_data, columns=[
                "Fecha y Hora",
                "Ciudad",
                "Latitud",
                "Longitud", 
                "Región",
                "País",
                "Temperatura Predicha (°C)",
                "Humedad Predicha (%)",
                "Viento (km/h)",
                "Nubosidad (%)",
                "Índice UV",
                "Amanecer",
                "Atardecer",
                "Fase Lunar",
            ])

            # Crear archivo Excel temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                temp_file_path = Path(tmp_file.name)
                with pd.ExcelWriter(temp_file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Reporte Meteorológico')
                    worksheet = writer.sheets['Reporte Meteorológico']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            # Nombre del archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_meteorologico_completo_{timestamp}.xlsx"

            return FileResponse(
                path=temp_file_path, 
                filename=filename, 
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except HTTPException:
            raise  # Permitir que FastAPI maneje las HTTPException como 401 o 404

        except Exception as e:
            print(f"Error en export_data_excel: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Ocurrió un error inesperado al generar el reporte. Inténtalo nuevamente más tarde."
            )
