# config.py - Archivo de configuración
"""
Configuración global para el sistema de predicción de series temporales.
"""

CONFIG = {
    # Parámetros temporales
    "TIEMPO": {
        "DIA_SEGUNDOS": 24 * 60 * 60,
        "YEAR_FACTOR": 365.2425,
    },
    # Parámetros de secuencia
    "SECUENCIA": {
        "INPUT_LENGTH": 24,
        "OUTPUT_LENGTH": 24,
    },
    # Parámetros de entrenamiento
    "ENTRENAMIENTO": {
        "EPOCHS": 80,
        "BATCH_SIZE": 256,
        "LEARNING_RATE": 5e-5,
        "LSTM_UNITS": 128,
    },
    # Parámetros de división de datos
    "DATOS": {
        "TRAIN_SIZE": 0.8,
        "VAL_SIZE": 0.1,
        "TEST_SIZE": 0.1,
    },
    # Columna objetivo
    "TARGET_COL": ["temp_c", "humidity"],
    # Rutas para guardar modelos y resultados
    "RUTAS": {
        "MODELO": "data_train/modelo_lstm.keras",
        "SCALER": "data_train/scalers.pkl",
        "RESULTADOS": "data_train/resultados_modelo.csv",
        "DATOS": "Data/datos_entrenamiento.csv",
        "INTENT_PATTERNS": "Data/intent_patterns.json",
        "RESPONSES": "Data/responses.json",
    },
}
