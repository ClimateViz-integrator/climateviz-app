import pandas as pd
import numpy as np
# Funcion para leer archivo csv

class DataReader: 

    def read_data(self, file_path):
        file_type = file_path.split('.')[-1]
        if file_type == 'csv':
            return pd.read_csv(file_path)
        elif file_type == 'xlsx':
            return pd.read_excel(file_path)
        elif file_type == 'json':
            return pd.read_json(file_path)
        elif file_type == 'xml':
            return pd.read_xml(file_path)
        elif file_type == 'txt':
            return pd.read_txt(file_path)
        elif file_type == 'pdf':
            return pd.read_pdf(file_path)
        elif file_type == 'docx':
            return pd.read_docx(file_path)
        else:
            return None
        
    def clean_data(self, data):
        
        data.dropna(axis=0)
        float_cols = data.select_dtypes(include=['float64']).columns
        data[float_cols] = data[float_cols].astype(np.float32)

        # Convertir ints de 64 bits a 32 o 16 bits según el rango de valores
        int_cols = data.select_dtypes(include=['int64']).columns
        for col in int_cols:
            if data[col].max() < np.iinfo(np.int16).max:  # Si los valores caben en int16
                data[col] = data[col].astype(np.int16)
            else:
                data[col] = data[col].astype(np.int32)  # Si no, usar int32
        return data

        


        

    