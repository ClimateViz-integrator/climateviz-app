import datetime
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler  # <-- Nuevo import
from Controllers.save_predictions import SavePredictions
from Controllers.data_reader import DataReader
from Controllers.clima_api import get_data, get_data_history
from Controllers.data_to_save import DataToSave
import joblib  # <-- Para guardar scaler y modelo juntos

class ModelIa:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "..", "Data", "train_model")
    MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
    SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")  # <-- Ruta del scaler
    
    def __init__(self, url_data=""):
        self.data = DataReader().read_data(url_data)
        self.data = DataReader().clean_data(self.data)
        self.data_df = pd.DataFrame(self.data)
        
        self.define_variables()
        self.scaler = StandardScaler()
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        if os.path.exists(self.MODEL_PATH) and os.path.exists(self.SCALER_PATH):
            self.model = joblib.load(self.MODEL_PATH)
            self.scaler = joblib.load(self.SCALER_PATH)
        else:
            self.train_model()
            joblib.dump(self.model, self.MODEL_PATH)
            joblib.dump(self.scaler, self.SCALER_PATH)
    
    def define_variables(self):
        self.data_df["last_updated"] = pd.to_datetime(self.data_df["last_updated"])
        min_date = self.data_df["last_updated"].min()
        self.data_df["days_since_start"] = (
            self.data_df["last_updated"] - min_date
        ).dt.days
        
        self.x = self.data_df.drop(["temp_c", "humidity", "last_updated", "us_epa_index", "gb_defra_index", "co","o3","no2","so2","pm2_5","pm10"], axis=1)
        self.y = self.data_df[["temp_c", "humidity", ]]
        self.x = self.x.apply(pd.to_numeric, errors="coerce")
        
    def train_model(self):
        X_train, X_test, y_train, y_test = train_test_split(self.x, self.y, test_size=0.2, random_state=42)
        
        # Ajustar scaler solo en X_train y transformar ambos
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model.fit(X_train_scaled, y_train)
        y_pred = self.model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        print(f"R² score in test of train: {r2:.2f}")
        mse = mean_squared_error(y_test, y_pred)
        print(f"Mean squared error in test of train: {mse:.2f}")
    
    def test(self, data):
        data_scaled = self.scaler.transform(data)
        pr = self.model.predict(data_scaled)
        r2 = r2_score(self.y, pr)
        print(f"R² score in test: {r2:.2f}")
        mse = mean_squared_error(self.y, pr)
        print(f"Mean squared error en prueba: {mse:.2f}")
    
    def predict_future(self, x, days_future):
        last_day = self.x["days_since_start"].max()
        x["days_since_start"] = last_day + days_future
        x["humidity"] = x["humidity"].astype(float)
        x["perceived_humidity"]= (x["humidity"] + np.random.uniform(-2, 2)).round(2)
        # eliminar humidity de x
        x = x.drop("humidity", axis=1)
        x = x.reindex(columns=self.x.columns, fill_value=0)
        x_scaled = self.scaler.transform(x)
        predictions = self.model.predict(x_scaled)
        #self.test(predictions[0])  # Llamar a la función test con las predicciones
        return pd.DataFrame(predictions, columns=["temp_c", "humidity",])
    
    async def prediction_weather_future(self, city, days_future, db):
        data = get_data(city)  # Obtener datos actuales
        history = get_data_history(city, days_future)  # Obtener datos históricos
        predictions_list = []
        date_futures = []
        all_ids = []  # Lista para almacenar todos los IDs
        
        # Obtener la fecha inicial a partir de los datos actuales
        current_datetime = datetime.datetime.strptime(data[0][22], "%Y-%m-%d %H:%M")
        
        # Si days_future es 0, se predice solo para el día actual
        if days_future == 0:
            future_date = current_datetime  # Se mantiene la fecha actual
            city_data, ids = DataToSave().prepare_input_data(data, db)
            all_ids.extend(ids)  # Guardamos los IDs para usarlos después
            city_df = DataToSave().create_dataframe_from_array(city_data)
            prediction = self.predict_future(city_df, days_future)  # Predicción para hoy
            
            predictions_list.append(prediction)
            date_futures.append(future_date)
        else:
            # Iterar sobre cada conjunto de datos históricos (día)
            for i in range(len(history)):
                future_date = current_datetime + datetime.timedelta(days=i)
                date_futures.append(future_date)
                
                # Preparar datos para la predicción
                city_data, ids = DataToSave().prepare_input_data([history[i]], db)
                all_ids.extend(ids)  # Guardamos los IDs en el mismo orden que las predicciones
                city_df = DataToSave().create_dataframe_from_array(city_data)
                
                # Predecir usando el modelo IA con los datos correspondientes a ese día
                prediction = self.predict_future(city_df, i)
                predictions_list.append(prediction)

                
        
        # Unir todas las predicciones en un DataFrame
        predictions_df = pd.concat(predictions_list, ignore_index=True)
        
        # Guardar en la base de datos y devolver los resultados
        data_predictions = SavePredictions().save_info(data, predictions_df, date_futures, all_ids, db)
        return data_predictions

