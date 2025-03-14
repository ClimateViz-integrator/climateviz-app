import datetime
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from Controllers.save_predictions import SavePredictions
from Controllers.data_reader import DataReader
from Controllers.clima_api import get_data
from Controllers.save_model import SaveModel
from Controllers.load_model import LoadModel
from Controllers.data_to_save import DataToSave

class ModelIa:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "..", "Data", "train_model")
    MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
    
    def __init__(self, url_data=""):
        self.data = DataReader().read_data(url_data)
        self.data = DataReader().clean_data(self.data)
        self.data_df = pd.DataFrame(self.data)
        
        self.define_variables()
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        
        if os.path.exists(self.MODEL_PATH):
            self.model = LoadModel().load_model()
        else:
            self.train_model()
            SaveModel().save_model(self.model)
        
        y_pred = self.prediction()
        mse, r2 = self.evaluate(y_pred)
        print(f"Mean squared error: {mse:.2f}")
        print(f"Coefficient of determination R²: {r2:.2f}")
    
    def define_variables(self):
        self.data_df["last_updated"] = pd.to_datetime(self.data_df["last_updated"])
        min_date = self.data_df["last_updated"].min()
        self.data_df["days_since_start"] = (
            self.data_df["last_updated"] - min_date
        ).dt.days
        
        
        # Crear nueva variable de humedad percibida
        self.data_df['perceived_humidity'] = (self.data_df['humidity'] + np.random.uniform(-2, 2, size=len(self.data_df))).round(2)
        
        self.x = self.data_df.drop(["temp_c", "humidity", "last_updated", "us_epa_index","gb_defra_index",], axis=1)
        self.y = self.data_df[["temp_c", "humidity"]]
        self.x = self.x.apply(pd.to_numeric, errors="coerce")
        
    def train_model(self):
        X_train, X_test, y_train, y_test = train_test_split(self.x, self.y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        print("R^2:", r2_score(y_test, y_pred))
    
    def prediction(self):
        return self.model.predict(self.x)
    
    def evaluate(self, y_pred):
        mse = mean_squared_error(self.y, y_pred)
        r2 = r2_score(self.y, y_pred)
        return mse, r2
    
    def test(self, data):
        return self.model.predict(data)
    
    def predict_future(self, x, days_future):
        last_day = self.x["days_since_start"].max()
        x["days_since_start"] = last_day + days_future
        x["humidity"] = x["humidity"].astype(float)
        x["perceived_humidity"]= (x["humidity"] + np.random.uniform(-2, 2)).round(2)
        # eliminar humidity de x
        x = x.drop("humidity", axis=1)
        x = x.reindex(columns=self.x.columns, fill_value=0)
        predictions = self.model.predict(x)
        return pd.DataFrame(predictions, columns=["temp_c", "humidity"])
    
    async def prediction_weather_future(self, city, days_future, db):
        data = get_data(city)
        data_api, city_data = DataToSave().prepare_input_data(data, db)
        current_datetime = datetime.datetime.strptime(data[0][22], "%Y-%m-%d %H:%M")
        date_future = current_datetime + datetime.timedelta(days=days_future)
        city_df = DataToSave().create_dataframe_from_array(city_data)
        prediction = self.predict_future(city_df, days_future)
        data_predictions = SavePredictions().save_info(data, prediction, date_future, data_api, db)
        return data_predictions
