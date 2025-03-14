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
        
        return data.dropna(axis=0)

        

    