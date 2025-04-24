# preprocessor.py - Clase para preprocesamiento de datos
"""
Módulo para el preprocesamiento de series temporales.
Incluye generación de características cíclicas y transformación de variables.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pickle
from Helper.config import CONFIG

class TimeSeriesPreprocessor:
    """
    Clase para el preprocesamiento de series temporales meteorológicas.
    """
    
    def __init__(self):
        """Inicializa el preprocesador con configuraciones predeterminadas."""
        self.dia_segundos = CONFIG['TIEMPO']['DIA_SEGUNDOS']
        self.year_segundos = CONFIG['TIEMPO']['DIA_SEGUNDOS'] * CONFIG['TIEMPO']['YEAR_FACTOR']
        self.feature_scalers = None
        self.target_scalers = {}  # Ahora es un diccionario para múltiples variables objetivo
        
    def add_cyclical_features(self, df, tiempo_s_col):
        """
        Añade características cíclicas de tiempo (seno y coseno para día y año).
        
        Args:
            df: DataFrame con datos meteorológicos
            tiempo_s_col: Serie con tiempo en segundos
            
        Returns:
            DataFrame con características cíclicas añadidas
        """
        
        df_copy = df.copy()
        
        # Añadir características cíclicas diarias y anuales
        df_copy['dia_sin'] = np.sin(tiempo_s_col * (2 * np.pi / self.dia_segundos))
        df_copy['dia_cos'] = np.cos(tiempo_s_col * (2 * np.pi / self.dia_segundos))
        df_copy['year_sin'] = np.sin(tiempo_s_col * (2 * np.pi / self.year_segundos))
        df_copy['year_cos'] = np.cos(tiempo_s_col * (2 * np.pi / self.year_segundos))
        
        return df_copy
    
    def process_wind_data(self, df):
        """
        Transforma las variables de viento de coordenadas polares a cartesianas.
        
        Args:
            df: DataFrame con datos meteorológicos que incluye 'wind_degree' y 'wind_kph'
            
        Returns:
            DataFrame con componentes cartesianas del viento
        """
        df_copy = df.copy()
        
        # Convertir dirección del viento a componentes cartesianas
        w_dir_rad = df_copy['wind_degree'] * np.pi/180
        df_copy['wx'] = df_copy['wind_kph'] * np.cos(w_dir_rad)
        df_copy['Wy'] = df_copy['wind_kph'] * np.sin(w_dir_rad)
        
        # Eliminar columnas originales
        df_copy = df_copy.drop(columns=['wind_degree', 'wind_kph'], axis=1)
        
        return df_copy
    
    def fit_scalers(self, data, features_to_scale=None, temporal_features=None):
        """
        Ajusta los escaladores para las características.
        
        Args:
            data: Datos para ajustar los escaladores
            features_to_scale: Índices de las características a escalar
            temporal_features: Índices de las características temporales (no escalar)
            
        Returns:
            self para encadenamiento de métodos
        """
        n_features = data.shape[2]
        
        # Si no se especifican, determinar automáticamente
        if temporal_features is None:
            temporal_features = list(range(4, 8))  # Características cíclicas por defecto
            
        if features_to_scale is None:
            features_to_scale = list(range(4)) + list(range(8, n_features))
        
        # Crear escaladores
        self.feature_scalers = [MinMaxScaler(feature_range=(-1, 1)) for _ in range(n_features)]
        self.temporal_features = temporal_features
        self.features_to_scale = features_to_scale
        
        # Ajustar escaladores para cada característica
        for i in features_to_scale:
            # Reshape para el escalador
            flat_feature = data[:, :, i].reshape(-1, 1)
            self.feature_scalers[i].fit(flat_feature)
        
        return self
        
    def scale_features(self, data):
        """
        Escala las características usando los escaladores ajustados.
        
        Args:
            data: Datos para escalar
            
        Returns:
            Datos escalados
        """
        if self.feature_scalers is None:
            raise ValueError("Los escaladores no han sido ajustados. Llame a fit_scalers primero.")
            
        scaled_data = np.zeros_like(data)
        
        # Escalar características
        for i in self.features_to_scale:
            flat_feature = data[:, :, i].reshape(-1, 1)
            scaled_flat = self.feature_scalers[i].transform(flat_feature)
            scaled_data[:, :, i] = scaled_flat.reshape(data.shape[0], -1)
        
        # Mantener características temporales sin cambios
        for i in self.temporal_features:
            scaled_data[:, :, i] = data[:, :, i]
            
        return scaled_data
    
    def fit_target_scaler(self, target_data, target_names):
        """
        Ajusta los escaladores para múltiples variables objetivo.

        Args:
            target_data: Array de forma (n_samples, output_length, n_targets)
            target_names: Lista de nombres de las variables objetivo (ej. ['temp_c', 'humidity'])
        """
        self.target_scalers = {}
        n_targets = target_data.shape[2]
        for i, name in enumerate(target_names):
            scaler = MinMaxScaler(feature_range=(-1, 1))
            flat_target = target_data[:, :, i].reshape(-1, 1)
            scaler.fit(flat_target)
            self.target_scalers[name] = scaler
        return self
    
    def scale_target(self, target_data, target_names):
        """
        Escala los datos de la variable objetivo.
        
        Args:
            target_data: Datos de la variable objetivo
            
        Returns:
            Datos de la variable objetivo escalados
        """
        if not self.target_scalers:
            raise ValueError("Los escaladores de la variable objetivo no han sido ajustados. Llame a fit_target_scaler primero.")

        scaled_data = np.zeros_like(target_data)
        for i, name in enumerate(target_names):
            flat_target = target_data[:, :, i].reshape(-1, 1)
            scaled_flat = self.target_scalers[name].transform(flat_target)
            scaled_data[:, :, i] = scaled_flat.reshape(target_data.shape[0], -1)
        return scaled_data
    
    def inverse_scale_target(self, scaled_target, target_names):
        """
        Invierte el escalado de los datos de la variable objetivo.
        
        Args:
            scaled_target: Datos escalados de la variable objetivo
            
        Returns:
            Datos de la variable objetivo en su escala original
        """
        if not self.target_scalers:
            raise ValueError("Los escaladores de la variable objetivo no han sido ajustados.")

        original_data = np.zeros_like(scaled_target)
        for i, name in enumerate(target_names):
            flat_scaled = scaled_target[:, :, i].reshape(-1, 1)
            original_flat = self.target_scalers[name].inverse_transform(flat_scaled)
            original_data[:, :, i] = original_flat.reshape(scaled_target.shape[0], -1)
        return original_data
    
    def save_scalers(self, filepath):
        """
        Guarda los escaladores en un archivo para uso posterior.
        
        Args:
            filepath: Ruta del archivo para guardar los escaladores
        """
        scalers_dict = {
            'feature_scalers': self.feature_scalers,
            'target_scalers': self.target_scalers,
            'temporal_features': self.temporal_features,
            'features_to_scale': self.features_to_scale
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(scalers_dict, f)
    
    def load_scalers(self, filepath):
        """
        Carga los escaladores desde un archivo.
        
        Args:
            filepath: Ruta del archivo con los escaladores guardados
            
        Returns:
            self para encadenamiento de métodos
        """
        with open(filepath, 'rb') as f:
            scalers_dict = pickle.load(f)
            
        self.feature_scalers = scalers_dict['feature_scalers']
        self.target_scalers = scalers_dict['target_scalers']
        self.temporal_features = scalers_dict['temporal_features']
        self.features_to_scale = scalers_dict['features_to_scale']
        
        return self