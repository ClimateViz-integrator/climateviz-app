import datetime
import os
from Controllers.save_predictions import SavePredictions
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
from models.tables import Input_data, Predictions
from Controllers.data_reader import DataReader
from Controllers.clima_api import get_data
from Controllers.save_model import SaveModel
from Controllers.load_model import LoadModel
import matplotlib.pyplot as plt
from fastapi.responses import FileResponse
import tempfile


class ModelIa:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "..", "Data", "train_model")
    MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
    POLY_PATH = os.path.join(MODEL_DIR, "poly.pkl")

    def __init__(self, url_data=""):
        self.degree = 2
        self.data = DataReader().read_data(url_data)
        self.data = DataReader().clean_data(self.data)
        self.data_df = pd.DataFrame(self.data)

        self.x = None
        self.y = None
        self.poly = PolynomialFeatures(degree=self.degree)
        self.define_variables()

        self.model = LinearRegression()
        if os.path.exists(self.MODEL_PATH) and os.path.exists(self.POLY_PATH):
            self.model, self.poly = LoadModel().load_model()
        else:
            self.train_model()
            SaveModel().save_model(self.model, self.poly)

        y_predic = self.prediction()
        mse, r2 = self.evaluate(y_predic)
        print("Mean squared error: %.2f" % mse)
        print("Coefficient of determination R²: %.2f" % r2)

    def define_variables(self):
        self.y = self.data_df[["temp_c", "pressure_mb", "precip_mm", "humidity", "cloud", "vis_km", "uv", "co", "o3", "no2", "so2"]]

        self.data_df["last_updated"] = pd.to_datetime(self.data_df["last_updated"])
        min_date = self.data_df["last_updated"].min()
        self.data_df["days_since_start"] = (
            self.data_df["last_updated"] - min_date
        ).dt.days

        self.x = self.data_df.drop(["temp_c", "last_updated"], axis=1)
        self.x = self.x.apply(pd.to_numeric, errors="coerce")

    def train_model(self):
        x_poly = self.poly.fit_transform(self.x)
        self.model.fit(x_poly, self.y)
        return x_poly

    def prediction(self):
        x_poly = self.poly.transform(self.x)
        return self.model.predict(x_poly)

    def evaluate(self, y_predic):
        mse = mean_squared_error(self.y, y_predic)
        r2 = r2_score(self.y, y_predic)
        return mse, r2

    def test(self, data):
        data = self.poly.transform(data)
        return self.model.predict(data)

    def _prepare_input_data(self, data, db):
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
        city_data = np.array([[data[0][i] for i in range(19)]])

        return data_api, city_data

    def _create_dataframe_from_array(self, city_data):
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
            "us_epa_index",
            "gb_defra_index",
        ]
        return pd.DataFrame(city_data, columns=columns)

    def predict_future(self, x, days_future):
        last_day = self.x["days_since_start"].max()
        x["days_since_start"] = last_day + days_future

        x = x.reindex(columns=self.x.columns, fill_value=0)
        x_poly = self.poly.transform(x)
        
        predictions = self.model.predict(x_poly)  # Ahora predice múltiples valores
        
        # Convertir a DataFrame con nombres de columnas
        prediction_df = pd.DataFrame(predictions, columns=["temp_c", "pressure_mb", "precip_mm", "humidity", "cloud", "vis_km", "uv", "co", "o3", "no2", "so2"])
        
        return prediction_df

    def prediction_weather_future(self, city, days_future, db):
        data = get_data(city)
        data_api, city_data = self._prepare_input_data(data, db)

        # Convert the string to a datetime object first
        current_datetime = datetime.datetime.strptime(data[0][22], "%Y-%m-%d %H:%M")

        # Now create your future date
        date_future = current_datetime + datetime.timedelta(days=days_future)

        city_df = self._create_dataframe_from_array(city_data)
        prediction = self.predict_future(city_df, days_future)

        data_predictions = SavePredictions().save_info(data, prediction, date_future, data_api, db)

        return data_predictions
   



    # def plot_training_results(self):
    #     """Genera gráficos de las variables entrenadas con los valores reales vs. predicciones."""
    #     y_predic = self.prediction()
    #     variables = self.y.columns  # Obtiene los nombres de las variables

    #     plt.figure(figsize=(15, 10))  # Tamaño del gráfico

    #     for i, var in enumerate(variables, 1):
    #         plt.subplot(4, 3, i)  # Organiza en una cuadrícula de subgráficos (hasta 12 variables)
    #         plt.scatter(self.x["days_since_start"], self.y[var], color="blue", label="Datos reales", alpha=0.5)
    #         plt.plot(self.x["days_since_start"], y_predic[:, i-1], color="red", label="Predicción")
    #         plt.xlabel("Días desde inicio")
    #         plt.ylabel(var)
    #         plt.title(f"Real vs Predicción: {var}")
    #         plt.legend()

    #     plt.tight_layout()
    #     plt.show()
