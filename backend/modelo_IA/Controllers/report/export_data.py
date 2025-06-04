from models.tables import Hour as Predictions, Forecast
import pandas as pd
from fastapi.responses import FileResponse
import tempfile
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

class ReportController:

    def export_data_excel(self, db: Session):
        """
        Exporta los datos extendidos a un archivo Excel y lo devuelve para su descarga.
        """
        try:
            # Obtener todas las horas con su forecast relacionado usando JOIN
            predictions_with_forecast = db.query(Predictions).join(Forecast).all()
            
            if not predictions_with_forecast:
                raise ValueError("No hay datos disponibles para exportar")
            
            # Construir datos extendidos
            extended_data = []
            for pred in predictions_with_forecast:
                forecast = pred.forecast
                
                # Extraer datos de location JSON
                location = forecast.location or {}
                lat = location.get('lat', 'N/A')
                lon = location.get('lon', 'N/A')
                region = location.get('region', 'N/A')
                country = location.get('country', 'N/A')

                
                # Extraer datos astronómicos
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

            # Crear DataFrame con columnas extendidas
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

            # Crear un archivo temporal en formato Excel
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                temp_file_path = Path(tmp_file.name)
                
                # Usar ExcelWriter para mejor formato
                with pd.ExcelWriter(temp_file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Reporte Meteorológico')
                    
                    # Obtener el workbook y worksheet para formato
                    workbook = writer.book
                    worksheet = writer.sheets['Reporte Meteorológico']
                    
                    # Ajustar ancho de columnas automáticamente
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

            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_meteorologico_completo_{timestamp}.xlsx"

            # Retornar el archivo para descarga
            return FileResponse(
                path=temp_file_path, 
                filename=filename, 
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            print(f"Error en export_data_excel: {str(e)}")
            raise e

    def export_data_excel_simple(self, db: Session):
        """
        Versión simplificada del reporte (tu versión original)
        """
        try:
            predictions = db.query(Predictions).all()
            
            if not predictions:
                raise ValueError("No hay datos disponibles para exportar")
            
            data = [[
                pred.date_time, pred.wind_kph, pred.cloud, pred.uv, pred.temp_pred,
                pred.humidity_pred
            ] for pred in predictions]

            df = pd.DataFrame(data, columns=[
                "Fecha y Hora", "Viento (km/h)", "Nubosidad", "Índice UV", 
                "Temperatura Predicha (°C)", "Humedad Predicha (%)"
            ])

            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                temp_file_path = Path(tmp_file.name)
                df.to_excel(temp_file_path, index=False, engine='openpyxl')

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_meteorologico_simple_{timestamp}.xlsx"

            return FileResponse(
                path=temp_file_path, 
                filename=filename, 
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            print(f"Error en export_data_excel_simple: {str(e)}")
            raise e
