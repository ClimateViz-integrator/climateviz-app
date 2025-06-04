

import os

import pandas as pd

from Controllers.model_build import TimeSeriesModel
from Etl.dataset import TimeSeriesDataset
from Etl.preprocessor import TimeSeriesPreprocessor
from Utils.config import CONFIG


class TrainOrLoadModel:
    """Clase para entrenar o cargar un modelo de series temporales."""

    def train_or_load_model(self):
        """Función principal para ejecutar el pipeline completo."""
        modelo_guardado = os.path.exists(CONFIG['RUTAS']['MODELO'])

        if modelo_guardado:
            print("Modelo ya entrenado encontrado. Cargando desde disco...")
            model = TimeSeriesModel()
            preprocessor = TimeSeriesPreprocessor()
            model.load()
            return model, preprocessor
        else:
            print("No se encontró modelo entrenado. Entrenando uno nuevo...")
            # 1. Cargar datos
            print("1. Cargando datos...")
            
            # Para este ejemplo, simulamos datos
            df = pd.read_csv(CONFIG['RUTAS']['DATOS'], index_col='datetime', parse_dates=['datetime'])
        
            # Calcular tiempo en segundos desde el inicio
            tiempo_s = df.index.map(pd.Timestamp.timestamp)
            
            # 2. Preprocesamiento
            print("2. Preprocesando datos...")
            preprocessor = TimeSeriesPreprocessor()
            
            # Añadir características cíclicas
            df = preprocessor.add_cyclical_features(df, tiempo_s)
            
            # Procesar datos de viento
            df = preprocessor.process_wind_data(df)
            
            # Resetear índice y eliminar columna datetime
            df = df.reset_index()
            df = df.drop(columns=['datetime'])
            
            # 3. Preparar conjuntos de datos
            print("3. Preparando conjuntos de datos...")
            dataset_handler = TimeSeriesDataset()
            data_dict = dataset_handler.prepare_dataset(df, target_col=CONFIG['TARGET_COL'])
            
            # 4. Escalar datos
            print("4. Escalando datos...")
            # Ajustar escaladores con datos de entrenamiento
            preprocessor.fit_scalers(data_dict['x_train'])
            preprocessor.fit_target_scaler(data_dict['y_train'], target_names=['temp_c', 'humidity'])
            
            # Escalar conjuntos de datos
            x_train_scaled = preprocessor.scale_features(data_dict['x_train'])
            x_val_scaled = preprocessor.scale_features(data_dict['x_val'])
            x_test_scaled = preprocessor.scale_features(data_dict['x_test'])
            
            y_train_scaled = preprocessor.scale_target(data_dict['y_train'], target_names=['temp_c', 'humidity'])
            y_val_scaled = preprocessor.scale_target(data_dict['y_val'], target_names=['temp_c', 'humidity'])
            y_test_scaled = preprocessor.scale_target(data_dict['y_test'], target_names=['temp_c', 'humidity'])
            
            # Guardar escaladores para uso posterior
            preprocessor.save_scalers(CONFIG['RUTAS']['SCALER'])
            
            # 5. Crear y entrenar modelo
            # 5. Crear o cargar modelo
            print("5. Entrenando modelo...")
            model = TimeSeriesModel()
            model.build_model(input_shape=(x_train_scaled.shape[1], x_train_scaled.shape[2]))
            model.train(x_train_scaled, y_train_scaled, x_val_scaled, y_val_scaled)
            # 6. Evaluar modelo
            print("6. Evaluando modelo...")
            metrics, y_pred = model.evaluate(x_test_scaled, y_test_scaled, scaler=preprocessor)
            
            # 7. Visualizar resultados
            print("7. Visualizando resultados...")
            # Graficar historia del entrenamiento
            if model.history:
                history_fig = model.plot_history()
                history_fig.savefig('data_train/historia_entrenamiento.png')
            else:
                print("No hay historial de entrenamiento para graficar.")
            print("8. Guardando modelo...")
            model.save()  # Guardar modelo tras entrenamiento
            print("¡Proceso completo!")
        
            return model, preprocessor