
import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "Data", "train_model")  # Subimos un nivel y ubicamos Data/train_model
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
#POLY_PATH = os.path.join(MODEL_DIR, "poly.pkl")

class SaveModel:
    
    def save_model(self, model):
        joblib.dump(model, MODEL_PATH)
        #joblib.dump(poly, POLY_PATH)
        print("Modelo guardado correctamente.") # Data\train_model

