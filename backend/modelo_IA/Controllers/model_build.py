# model.py - Clase para el modelo de predicción
"""
Módulo que define el modelo de predicción de series temporales,
incluyendo arquitectura, entrenamiento y evaluación.
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from Utils.config import CONFIG

class TimeSeriesModel:
    """
    Clase para la creación, entrenamiento y evaluación de modelos de series temporales.
    """
    
    def __init__(self, units=None, learning_rate=None):
        """
        Inicializa el modelo.
        
        Args:
            units: Número de unidades en la capa LSTM
            learning_rate: Tasa de aprendizaje para el optimizador
        """
        self.units = units or CONFIG['ENTRENAMIENTO']['LSTM_UNITS']
        self.learning_rate = learning_rate or CONFIG['ENTRENAMIENTO']['LEARNING_RATE']
        self.model = None
        self.history = None
        
    def build_model(self, input_shape):
        """
        Construye la arquitectura del modelo.
        
        Args:
            input_shape: Forma de los datos de entrada (timesteps, features)
            
        Returns:
            self para encadenamiento de métodos
        """
        output_shape = CONFIG['SECUENCIA']['OUTPUT_LENGTH'] 
        # Definir función de pérdida RMSE
        def root_mean_squared_error(y_true, y_pred):
            return tf.sqrt(tf.reduce_mean(tf.square(y_pred - y_true)))
        
        # Crear modelo
        # model = Sequential([
        #     LSTM(self.units, input_shape=input_shape),
        #     Dense(CONFIG['SECUENCIA']['OUTPUT_LENGTH'], activation='linear')
        # ])
        model = Sequential()
        model.add(LSTM(self.units, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(BatchNormalization())
        model.add(Dense(output_shape, activation='linear'))
        model.add(tf.keras.layers.Reshape(output_shape, 2))
        
        # Compilar modelo
        model.compile(
            optimizer=RMSprop(learning_rate=self.learning_rate),
            loss=root_mean_squared_error
        )
        
        self.model = model
        return self
    
    def train(self, x_train, y_train, x_val, y_val, epochs=None, batch_size=None):
        """
        Entrena el modelo con los datos proporcionados.
        
        Args:
            x_train: Datos de entrada para entrenamiento
            y_train: Datos de salida para entrenamiento
            x_val: Datos de entrada para validación
            y_val: Datos de salida para validación
            epochs: Número de épocas para entrenamiento
            batch_size: Tamaño del lote para entrenamiento
            
        Returns:
            self para encadenamiento de métodos
        """
        if self.model is None:
            input_shape = (x_train.shape[1], x_train.shape[2])
            self.build_model(input_shape)
            
        epochs = epochs or CONFIG['ENTRENAMIENTO']['EPOCHS']
        batch_size = batch_size or CONFIG['ENTRENAMIENTO']['BATCH_SIZE']
        
        # Definir callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            ModelCheckpoint(
                filepath=CONFIG['RUTAS']['MODELO'],
                monitor='val_loss',
                save_best_only=True
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6
            )
        ]
        
        # Entrenar modelo
        self.history = self.model.fit(
            x=x_train,
            y=y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(x_val, y_val),
            callbacks=callbacks,
            verbose=2
        )
        
        return self
    
    def predict(self, x):
        """
        Realiza predicciones con el modelo entrenado.
        
        Args:
            x: Datos de entrada para predicción
            
        Returns:
            Predicciones del modelo
        """
        if self.model is None:
            raise ValueError("El modelo no ha sido entrenado. Llame a train primero.")
            
        return self.model.predict(x)
    
    def evaluate(self, x_test, y_test, scaler=None):
        if self.model is None:
            raise ValueError("El modelo no ha sido entrenado. Llame a train primero.")

        y_pred = self.predict(x_test)

        if scaler is not None:
            y_test_orig = scaler.inverse_scale_target(y_test, ['temp_c', 'humidity']).squeeze()
            y_pred_orig = scaler.inverse_scale_target(y_pred, ['temp_c', 'humidity']).squeeze()
        else:
            y_test_orig = y_test
            y_pred_orig = y_pred

        mae = np.mean(np.abs(y_pred_orig - y_test_orig))
        rmse = np.sqrt(np.mean(np.square(y_pred_orig - y_test_orig)))
        r2 = r2_score(y_test_orig.reshape(-1, 2), y_pred_orig.reshape(-1, 2))

        metrics = {
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        }

        print(f'MAE: {mae:.4f}')
        print(f'RMSE: {rmse:.4f}')
        print(f'R^2: {r2:.4f}')
        return metrics, y_pred_orig
    
    def plot_history(self):
        """
        Grafica la historia del entrenamiento.
        
        Returns:
            Figura de matplotlib
        """
        if self.history is None:
            raise ValueError("El modelo no ha sido entrenado. Llame a train primero.")
            
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(self.history.history['loss'], label='Train Loss')
        ax.plot(self.history.history['val_loss'], label='Validation Loss')
        ax.set_xlabel('Época')
        ax.set_ylabel('Pérdida (RMSE)')
        ax.set_title('Historia del Entrenamiento')
        ax.legend()
        plt.grid(True)
        
        return fig
    
    def plot_predictions(self, y_true, y_pred):
        import matplotlib.pyplot as plt

        y_true = np.squeeze(y_true)
        y_pred = np.squeeze(y_pred)

        if y_true.ndim == 2:
            y_true = np.expand_dims(y_true, axis=-1)
        if y_pred.ndim == 2:
            y_pred = np.expand_dims(y_pred, axis=-1)

        num_variables = y_true.shape[-1]
        fig, axs = plt.subplots(num_variables, 1, figsize=(12, 4 * num_variables), sharex=True)
        if num_variables == 1:
            axs = [axs]

        for var in range(num_variables):
            for t in range(y_true.shape[1]):
                axs[var].plot(y_true[:, t, var], label=f'Real t+{t+1}' if t == 0 else "")
                axs[var].plot(y_pred[:, t, var], linestyle='--', label=f'Pred t+{t+1}' if t == 0 else "")
            axs[var].set_title(f'Variable {var+1}')
            axs[var].legend()
            axs[var].grid(True)

        plt.tight_layout()
        return fig

    
    def save(self, filepath=None):
        """
        Guarda el modelo entrenado.
        
        Args:
            filepath: Ruta del archivo para guardar el modelo
        """
        if self.model is None:
            raise ValueError("El modelo no ha sido entrenado. Llame a train primero.")
            
        filepath = filepath or CONFIG['RUTAS']['MODELO']
        self.model.save(filepath)
        print(f"Modelo guardado en: {filepath}")
    
    def load(self, filepath=None):
        """
        Carga un modelo previamente entrenado.
        
        Args:
            filepath: Ruta del archivo con el modelo guardado
            
        Returns:
            self para encadenamiento de métodos
        """
        filepath = filepath or CONFIG['RUTAS']['MODELO']
        
        # Definir función de pérdida personalizada
        def root_mean_squared_error(y_true, y_pred):
            return tf.sqrt(tf.reduce_mean(tf.square(y_pred - y_true)))
        
        # Cargar modelo con función de pérdida personalizada
        # self.model = load_model(filepath, custom_objects={
        #     'root_mean_squared_error': root_mean_squared_error,
        # })
        self.model = load_model(
            filepath,
            custom_objects={'root_mean_squared_error': root_mean_squared_error},
            compile=False  # <-- correcto aquí
        )

        return self