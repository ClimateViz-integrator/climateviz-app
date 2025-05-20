import json
import pandas as pd
import os

def readFile(path):
    """
    Lee un archivo JSON, CSV, TXT o Excel y retorna su contenido.
    Para JSON retorna un dict.
    Para CSV y Excel retorna un DataFrame.
    Para TXT retorna una lista de líneas (str).
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"El archivo '{path}' no existe.")

    ext = os.path.splitext(path)[1].lower()

    try:
        if ext == ".json":
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        elif ext == ".csv":
            return pd.read_csv(path)
        elif ext in [".xls", ".xlsx"]:
            return pd.read_excel(path)
        elif ext == ".txt":
            with open(path, "r", encoding="utf-8") as file:
                return file.readlines()
        else:
            raise ValueError(f"Extensión de archivo no soportada: {ext}")
    except Exception as e:
        raise RuntimeError(f"Error al leer el archivo '{path}': {e}")
