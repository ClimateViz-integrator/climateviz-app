# main.py - Script principal para ejecutar el sistema completo
"""
Script principal que integra todos los componentes para
el entrenamiento y evaluación del modelo de predicción.
"""
import asyncio
import pandas as pd
from Controllers.save_predictions import SavePredictions
from Controllers.weather_api import (
    extract_additional_info,
    extract_hourly_data,
    get_data,
)
from fastapi import HTTPException
import numpy as np
import tensorflow as tf
import os
from Utils.config import CONFIG
from Etl.preprocessor import TimeSeriesPreprocessor
from Etl.dataset import TimeSeriesDataset
from Controllers.train_or_load_model import TrainOrLoadModel


class PredictionController:
    """Clase para manejar la predicción del clima utilizando un modelo de series temporales."""

    def __init__(self):
        self.set_seeds()
        self.model, self.preprocessor = (
            TrainOrLoadModel().train_or_load_model()
        )  # Entrenar o cargar el modelo al iniciar la clase

    # Configurar semillas para reproducibilidad
    def set_seeds(self, seed=123):
        tf.random.set_seed(seed)
        np.random.seed(seed)
        tf.config.experimental.enable_op_determinism()
        os.environ["TF_DETERMINISTIC_OPS"] = "1"

    async def predict_from_api(self, city, days, db, user_id=None):

        if user_id is None and days > 2:
            raise HTTPException(
                    status_code=401,
                    detail="Debe estar autenticado para generar una predicción por más de 2 días. Por favor, inicie sesión o regístrese. 🔐"
                )

        total_hours = days * 24
        if 1 <= days <= 6:
            days += 2
        print(f"🌦️ Obteniendo datos de clima desde la API para {city}...")

        # 1. Obtener datos de la API
        datos_api = get_data(city, days)
        df_clima = extract_hourly_data(datos_api)
        df_clima = df_clima.sort_index()
        df_clima = df_clima[~df_clima.index.duplicated(keep="last")]
        info_adicional = extract_additional_info(city, days)

        # 2. Preprocesamiento
        tiempo_s = df_clima.index.map(pd.Timestamp.timestamp)
        self.preprocessor = TimeSeriesPreprocessor()
        self.preprocessor.load_scalers(CONFIG["RUTAS"]["SCALER"])
        df_clima_proc = self.preprocessor.add_cyclical_features(
            df_clima.copy(), tiempo_s
        )
        df_clima_proc = self.preprocessor.process_wind_data(df_clima_proc)

        # 3. Crear secuencias y escalar
        dataset_handler = TimeSeriesDataset()
        x_seq, _ = dataset_handler.create_sequences(
            df_clima_proc, target_col=CONFIG["TARGET_COL"]
        )
        if x_seq is None or len(x_seq) == 0:
            raise ValueError(
                f"❌ No se pudieron generar secuencias de entrada. Se requieren al menos {CONFIG['SECUENCIA']['INPUT_LENGTH'] + CONFIG['SECUENCIA']['OUTPUT_LENGTH'] - 1} registros, pero se recibieron {len(df_clima_proc)}."
            )
        x_seq_scaled = self.preprocessor.scale_features(x_seq)

        pred_scaled = self.model.predict(x_seq_scaled)
        pred_original = self.preprocessor.inverse_scale_target(
            pred_scaled, target_names=["temp_c", "humidity"]
        )

        # 4. Construir dataframe con predicciones

        pred_original = pred_original.reshape(-1, pred_original.shape[-1])
        pred_original = pred_original[:total_hours]

        last_datetime = df_clima.index[-1]
        future_dates = pd.date_range(
            start=last_datetime + pd.Timedelta(hours=1),
            periods=len(pred_original),
            freq="H",
        )

        pred_df = pd.DataFrame(
            {
                "datetime": future_dates,
                "temp_pred": pred_original[:, 0],
                "humidity_pred": pred_original[:, 1],
            }
        )

        print("✅ Predicciones generadas correctamente.\n")
        pred_df.to_csv("data_train/predicciones.csv", index=False)

        # 5. Agrupar por días para la respuesta tipo API
        inserted_forecasts, info_adicional = await SavePredictions().save_predictions(
            pred_df, info_adicional, city, db, user_id=user_id
        )

        return inserted_forecasts, info_adicional
