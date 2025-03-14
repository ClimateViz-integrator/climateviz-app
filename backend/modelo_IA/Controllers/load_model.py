
import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "Data", "train_model")  # Subimos un nivel y ubicamos Data/train_model
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
#POLY_PATH = os.path.join(MODEL_DIR, "poly.pkl")

class LoadModel:
    def load_model(self):
        model = joblib.load(MODEL_PATH)
        #poly = joblib.load(POLY_PATH)
        print("Modelo cargado correctamente.")
        return model